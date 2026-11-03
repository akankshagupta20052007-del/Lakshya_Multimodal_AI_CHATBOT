# app/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db, engine
from ..schemas.common import HealthResponse
from ..services.rag_service import rag_service
from ..config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
@router.get("/api/health", response_model=HealthResponse)
def check_health(db: Session = Depends(get_db)):
    # Verify DB connectivity
    db_status = "connected"
    backend = "MySQL" if "mysql" in str(engine.url) else "SQLite Fallback"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    rag_stats = rag_service.get_stats()

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database_status=db_status,
        database_backend=backend,
        llm_provider=settings.LLM_PROVIDER,
        llm_model=settings.effective_model,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        indexed_documents_count=rag_stats["indexed_documents_count"],
        indexed_chunks_count=rag_stats["indexed_chunks_count"],
    )
