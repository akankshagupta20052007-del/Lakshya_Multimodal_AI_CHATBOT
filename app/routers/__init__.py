# app/routers/__init__.py
from .conversations import router as conversations_router
from .chat import router as chat_router
from .documents import router as documents_router
from .health import router as health_router
from .media import router as media_router

__all__ = [
    "conversations_router",
    "chat_router",
    "documents_router",
    "health_router",
    "media_router",
]
