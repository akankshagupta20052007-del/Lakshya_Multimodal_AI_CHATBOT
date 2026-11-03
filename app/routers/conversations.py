# app/routers/conversations.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    CitationSchema,
)
from ..schemas.common import APIResponse
from ..services.db_service import DatabaseService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate = ConversationCreate(),
    db: Session = Depends(get_db)
):
    conv = DatabaseService.create_conversation(db, title=payload.title)
    return ConversationResponse(
        conversation_id=conv.conversation_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )


@router.get("", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    conversations = DatabaseService.list_conversations(db, skip=skip, limit=limit)
    return conversations


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conv = DatabaseService.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    # Format messages and sources
    messages_dto = []
    for m in conv.messages:
        citations = [
            CitationSchema(
                document_id=s.document_id,
                source_title=s.source_title,
                chunk_reference=s.chunk_reference,
                snippet=s.snippet,
            )
            for s in m.sources
        ]
        messages_dto.append(
            MessageResponse(
                message_id=m.message_id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                input_type=m.input_type,
                created_at=m.created_at,
                sources=citations
            )
        )

    return ConversationDetailResponse(
        conversation_id=conv.conversation_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=messages_dto
    )


@router.delete("/{conversation_id}", response_model=APIResponse[dict])
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    success = DatabaseService.delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )
    return APIResponse(
        success=True,
        message=f"Conversation {conversation_id} deleted successfully",
        data={"conversation_id": conversation_id}
    )
