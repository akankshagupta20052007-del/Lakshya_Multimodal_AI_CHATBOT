# app/main.py
"""
FastAPI Backend Application for Nexus Multimodal AI Studio.
Mounts REST APIs and static media directories.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .utils.logging_config import logger
from .routers import (
    conversations_router,
    chat_router,
    documents_router,
    health_router,
    media_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Initializing {settings.APP_NAME} Backend...")
    try:
        init_db()
        logger.info("Database initialized successfully on startup.")
    except Exception as e:
        logger.error(f"Error during database startup initialization: {e}")
    yield
    logger.info("Shutting down Nexus Backend...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade Multimodal AI Studio with Gemini, RAG, Vision, Voice & Image Generation",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health_router)
app.include_router(conversations_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(media_router, prefix="/api")

# Mount Static Media Files (Generated Images and Synthesized Audio)
app.mount("/static/images", StaticFiles(directory=str(settings.resolved_images_dir)), name="images")
app.mount("/static/audio", StaticFiles(directory=str(settings.resolved_audio_dir)), name="audio")

# Mount Static Documentation (Project Reports, Architecture Specs)
docs_dir = settings.BASE_DIR / "data" / "generated" / "docs"
docs_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/docs", StaticFiles(directory=str(docs_dir)), name="docs")


@app.get("/", tags=["Root"])
def root():
    return JSONResponse({
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "status": "online",
        "documentation": "/docs",
        "health_check": "/api/health"
    })


if __name__ == "__main__":
    import uvicorn
    is_production = settings.APP_ENV.lower() == "production"
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=not is_production
    )
