# app/schemas/__init__.py
from .common import APIResponse, HealthResponse
from .chat import (
    CitationSchema,
    MessageCreate,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    ChatRequest,
    ChatResponse,
)
from .document import DocumentResponse, DocumentUploadResponse, DocumentChunk

__all__ = [
    "APIResponse",
    "HealthResponse",
    "CitationSchema",
    "MessageCreate",
    "MessageResponse",
    "ConversationCreate",
    "ConversationResponse",
    "ConversationDetailResponse",
    "ChatRequest",
    "ChatResponse",
    "DocumentResponse",
    "DocumentUploadResponse",
    "DocumentChunk",
]
