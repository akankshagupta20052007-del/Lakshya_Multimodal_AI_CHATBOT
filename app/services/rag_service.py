# app/services/rag_service.py
# Re-exports for backwards compatibility
from .rag import VectorStore, RAGService, rag_service

__all__ = ["VectorStore", "RAGService", "rag_service"]
