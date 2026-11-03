# app/services/db_service.py
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Conversation, Message, Document, MessageSource
from ..schemas import CitationSchema


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DatabaseService:
    @staticmethod
    def create_conversation(db: Session, title: Optional[str] = None) -> Conversation:
        conversation = Conversation(title=title or "New Conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
        return db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()

    @staticmethod
    def list_conversations(db: Session, skip: int = 0, limit: int = 50) -> List[dict]:
        """
        Returns list of conversations with message count.
        """
        results = (
            db.query(
                Conversation,
                func.count(Message.message_id).label("message_count")
            )
            .outerjoin(Message, Conversation.conversation_id == Message.conversation_id)
            .group_by(Conversation.conversation_id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        conversations = []
        for conv, count in results:
            conversations.append({
                "conversation_id": conv.conversation_id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": count
            })
        return conversations

    @staticmethod
    def update_conversation_title(db: Session, conversation_id: int, title: str) -> Optional[Conversation]:
        conv = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if conv:
            conv.title = title
            conv.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(conv)
        return conv

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int) -> bool:
        conv = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if not conv:
            return False
        db.delete(conv)
        db.commit()
        return True

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        input_type: str = "text",
        citations: Optional[List[CitationSchema]] = None,
        media_url: Optional[str] = None
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            input_type=input_type,
            media_url=media_url,
            created_at=utc_now()
        )
        db.add(message)
        db.flush()  # get message_id

        # Update parent conversation updated_at
        conv = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if conv:
            conv.updated_at = utc_now()

        if citations:
            for cit in citations:
                source = MessageSource(
                    message_id=message.message_id,
                    document_id=cit.document_id,
                    chunk_reference=cit.chunk_reference,
                    source_title=cit.source_title,
                    snippet=cit.snippet[:500] if cit.snippet else None
                )
                db.add(source)

        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_conversation_history(db: Session, conversation_id: int, limit: int = 20) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )

    # Document operations
    @staticmethod
    def create_document(
        db: Session,
        filename: str,
        document_type: str,
        processing_status: str = "indexed"
    ) -> Document:
        doc = Document(
            filename=filename,
            document_type=document_type,
            processing_status=processing_status,
            created_at=utc_now()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_document(db: Session, document_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.document_id == document_id).first()

    @staticmethod
    def list_documents(db: Session) -> List[Document]:
        return db.query(Document).order_by(Document.created_at.desc()).all()

    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        if not doc:
            return False
        db.delete(doc)
        db.commit()
        return True
