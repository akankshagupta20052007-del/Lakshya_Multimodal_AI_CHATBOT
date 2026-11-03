# app/schemas/document.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentResponse(BaseModel):
    document_id: int
    filename: str
    document_type: str
    processing_status: str
    created_at: datetime
    chunks_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    document_type: str
    chunks_indexed: int
    message: str


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: int
    document_title: str
    chunk_index: int
    text: str
    score: Optional[float] = None
