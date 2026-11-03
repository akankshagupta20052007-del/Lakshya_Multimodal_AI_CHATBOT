# app/database.py
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings, BASE_DIR

logger = logging.getLogger("multimodal_chatbot.database")

# Declarative Base for ORM Models
Base = declarative_base()


def get_engine():
    """
    Creates the SQLAlchemy engine.
    Uses configured DATABASE_URL or constructs MySQL URL from settings.
    If primary connection is unavailable and USE_SQLITE_FALLBACK is enabled,
    gracefully falls back to a persistent SQLite database.
    """
    db_url = settings.computed_database_url
    engine_kwargs = {
        "pool_pre_ping": True,
        "echo": False,
        "future": True,
    }
    if db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    try:
        engine = create_engine(db_url, **engine_kwargs)
        # Verify connection
        with engine.connect() as conn:
            logger.info(f"Connected to primary database successfully: {db_url.split('@')[-1]}")
        return engine
    except Exception as exc:
        if settings.USE_SQLITE_FALLBACK:
            sqlite_path = settings.resolved_sqlite_path
            fallback_url = f"sqlite:///{sqlite_path.as_posix()}"
            logger.warning(
                f"Could not connect to database at {db_url}. "
                f"Reason: {exc}. "
                f"Falling back to local SQLite database at: {sqlite_path}. "
                f"To use MySQL, ensure your MySQL service is running and credentials in .env are correct."
            )
            fallback_engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
                echo=False,
                future=True,
            )
            return fallback_engine
        else:
            logger.error(f"Failed to connect to database: {exc}")
            raise exc


# Global engine and sessionmaker
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def init_db():
    """Initializes tables in the configured database."""
    # Import all models to ensure they are registered with Base.metadata
    from .models import Conversation, Message, Document, MessageSource  # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def get_db():
    """
    FastAPI dependency that yields a SQLAlchemy database session and guarantees closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
