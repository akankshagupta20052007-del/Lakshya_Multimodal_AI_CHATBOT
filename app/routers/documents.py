# app/routers/documents.py
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.document import DocumentResponse, DocumentUploadResponse
from ..schemas.common import APIResponse
from ..services.db_service import DatabaseService
from ..services.rag_service import rag_service
from ..services.safety import safety_service
from ..config import settings

logger = logging.getLogger("multimodal_chatbot.documents")
router = APIRouter(prefix="/documents", tags=["Documents & RAG"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or "uploaded_document.txt"
    file_bytes = await file.read()

    # Enforce security validation
    is_valid, err_msg = safety_service.validate_upload(
        filename=filename,
        file_bytes=file_bytes,
        allowed_types=["pdf", "txt", "md"]
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    ext = filename.lower().split(".")[-1] if "." in filename else "txt"

    # Save to knowledge_base directory
    try:
        kb_path = settings.resolved_knowledge_base_dir / filename
        with open(kb_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        logger.warning(f"Could not write copy to knowledge_base: {e}")

    # 1. Register in database
    doc_record = DatabaseService.create_document(
        db=db,
        filename=filename,
        document_type=ext,
        processing_status="processing"
    )

    # 2. Extract, chunk, and index into VectorStore
    try:
        chunks_count, _ = rag_service.process_and_index_document(
            document_id=doc_record.document_id,
            filename=filename,
            file_bytes=file_bytes
        )
        doc_record.processing_status = "indexed"
        db.commit()
    except Exception as e:
        logger.error(f"Failed to process document {filename}: {e}")
        doc_record.processing_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error indexing document: {str(e)}"
        )

    return DocumentUploadResponse(
        document_id=doc_record.document_id,
        filename=filename,
        document_type=ext,
        chunks_indexed=chunks_count,
        message=f"Document successfully indexed into vector store with {chunks_count} chunks."
    )


@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = DatabaseService.list_documents(db)
    response = []
    # Count chunks per document in vector store
    chunk_counts = {}
    for c in rag_service.vector_store.chunks:
        d_id = c.get("document_id")
        chunk_counts[d_id] = chunk_counts.get(d_id, 0) + 1

    for d in docs:
        response.append(DocumentResponse(
            document_id=d.document_id,
            filename=d.filename,
            document_type=d.document_type,
            processing_status=d.processing_status,
            created_at=d.created_at,
            chunks_count=chunk_counts.get(d.document_id, 0)
        ))
    return response


@router.delete("/{document_id}", response_model=APIResponse[dict])
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = DatabaseService.get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # Remove from vector index
    rag_service.delete_document_index(document_id)

    # Remove from database
    DatabaseService.delete_document(db, document_id)

    return APIResponse(
        success=True,
        message=f"Document '{doc.filename}' and its vector embeddings were deleted.",
        data={"document_id": document_id}
    )
