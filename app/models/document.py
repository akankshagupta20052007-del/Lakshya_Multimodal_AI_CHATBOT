# app/models/document.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    filename = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # "pdf", "txt", etc.
    processing_status = Column(String(50), nullable=False, default="indexed")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    sources = relationship("MessageSource", back_populates="document")


class MessageSource(Base):
    __tablename__ = "message_sources"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message_id = Column(
        Integer,
        ForeignKey("messages.message_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    document_id = Column(
        Integer,
        ForeignKey("documents.document_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    chunk_reference = Column(String(255), nullable=True)  # e.g., "chunk_1" or section title
    source_title = Column(String(255), nullable=True)
    snippet = Column(String(500), nullable=True)

    # Relationships
    message = relationship("Message", back_populates="sources")
    document = relationship("Document", back_populates="sources")
