# app/config.py
import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application settings
    APP_NAME: str = Field("Lakshya Multimodal AI Studio", description="Name of the AI application")
    APP_ENV: str = Field("development", description="Environment: development, test, or production")
    API_HOST: str = Field("127.0.0.1", description="FastAPI host")
    API_PORT: int = Field(8000, description="FastAPI port")
    STREAMLIT_PORT: int = Field(8501, description="Streamlit port")
    CORS_ORIGINS: str = Field(
        "http://localhost:8501,http://127.0.0.1:8501,http://localhost:8000,http://127.0.0.1:8000",
        description="Comma-separated list of allowed CORS origins"
    )

    # Centralized Google Gemini Configuration
    GEMINI_API_KEY: str = Field("", description="Single centralized Google AI Studio Gemini API key")
    GEMINI_MODEL: str = Field("gemini-3.5-flash-lite", description="Primary Gemini model")
    POLLINATIONS_API_KEY: Optional[str] = Field(None, description="Optional Pollen API key for unlimited image generation")

    # Legacy alias support
    LLM_API_KEY: Optional[str] = Field(None, description="Legacy alias for GEMINI_API_KEY")
    LLM_MODEL: Optional[str] = Field(None, description="Legacy alias for GEMINI_MODEL")
    LLM_PROVIDER: str = Field("gemini", description="LLM provider: gemini or mock")

    # Database Configuration
    DB_DIALECT: str = Field("sqlite", description="Database dialect: 'sqlite' or 'mysql'")
    SQLITE_DB_PATH: str = Field("./data/chatbot.db", description="Path to SQLite database file")
    DATABASE_URL: Optional[str] = Field(None, description="Explicit SQLAlchemy database URL override")

    # MySQL connection configuration (if DB_DIALECT=mysql)
    MYSQL_HOST: str = Field("localhost", description="MySQL server host")
    MYSQL_PORT: int = Field(3306, description="MySQL server port")
    MYSQL_DATABASE: str = Field("multimodal_chatbot", description="MySQL database name")
    MYSQL_USER: str = Field("root", description="MySQL user")
    MYSQL_PASSWORD: str = Field("", description="MySQL password")
    USE_SQLITE_FALLBACK: bool = Field(True, description="Fall back to SQLite if MySQL is offline")

    # Embeddings & RAG Vector configuration
    EMBEDDING_PROVIDER: str = Field("local", description="Embedding provider: 'local' or 'gemini'")
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", description="Model name for embeddings")
    VECTOR_STORE_PATH: str = Field("./data/vector_index", description="Path to local vector index")
    MAX_UPLOAD_SIZE_MB: int = Field(10, description="Maximum upload size in Megabytes")
    SIMILARITY_THRESHOLD: float = Field(0.20, description="Minimum cosine similarity for RAG retrieval")
    TOP_K_CHUNKS: int = Field(3, description="Number of context chunks to retrieve for RAG")

    # Media storage paths
    GENERATED_IMAGES_PATH: str = Field("./data/generated/images", description="Storage directory for generated images")
    GENERATED_AUDIO_PATH: str = Field("./data/generated/audio", description="Storage directory for synthesized audio")
    KNOWLEDGE_BASE_PATH: str = Field("./knowledge_base", description="Storage directory for reference documents")

    @property
    def effective_api_key(self) -> str:
        """Returns the centralized Gemini API key, trimmed of any stray quotes or whitespace."""
        key = self.GEMINI_API_KEY or self.LLM_API_KEY or ""
        return key.strip(' "\'')

    @property
    def effective_model(self) -> str:
        """Returns the primary model name."""
        return self.GEMINI_MODEL or self.LLM_MODEL or "gemini-3.5-flash-lite"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def resolved_sqlite_path(self) -> Path:
        p = Path(self.SQLITE_DB_PATH)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.parent.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    @property
    def resolved_images_dir(self) -> Path:
        p = Path(self.GENERATED_IMAGES_PATH)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    @property
    def resolved_audio_dir(self) -> Path:
        p = Path(self.GENERATED_AUDIO_PATH)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    @property
    def resolved_knowledge_base_dir(self) -> Path:
        p = Path(self.KNOWLEDGE_BASE_PATH)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    @property
    def resolved_vector_path(self) -> Path:
        p = Path(self.VECTOR_STORE_PATH)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    @property
    def computed_database_url(self) -> str:
        """Constructs the database URL based on dialect and settings."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.DB_DIALECT.lower() == "sqlite":
            return f"sqlite:///{self.resolved_sqlite_path.as_posix()}"

        pwd = f":{self.MYSQL_PASSWORD}" if self.MYSQL_PASSWORD else ""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}{pwd}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4&connect_timeout=3"
        )


# Singleton settings instance
settings = Settings()

# Ensure critical directories exist
settings.resolved_images_dir
settings.resolved_audio_dir
settings.resolved_knowledge_base_dir
settings.resolved_vector_path
