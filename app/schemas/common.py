# app/schemas/common.py
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    database_status: str
    database_backend: str
    llm_provider: str
    llm_model: str
    embedding_provider: str
    indexed_documents_count: int
    indexed_chunks_count: int
