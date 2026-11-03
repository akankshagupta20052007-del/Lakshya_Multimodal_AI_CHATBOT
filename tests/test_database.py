# tests/test_database.py
import pytest
from app.database import SessionLocal, init_db
from app.services.db_service import DatabaseService
from app.schemas.chat import CitationSchema


@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_conversation_lifecycle(db_session):
    # Create conversation
    conv = DatabaseService.create_conversation(db_session, title="Test Conversation")
    assert conv.conversation_id is not None
    assert conv.title == "Test Conversation"

    # Add user message
    user_msg = DatabaseService.add_message(
        db_session,
        conversation_id=conv.conversation_id,
        role="user",
        content="What is in the documentation?",
        input_type="text"
    )
    assert user_msg.message_id is not None
    assert user_msg.role == "user"

    # Add assistant message with citation
    citation = CitationSchema(
        document_id=None,
        source_title="User Manual",
        chunk_reference="chunk_1",
        snippet="This is a test snippet from manual.",
        score=0.95
    )
    asst_msg = DatabaseService.add_message(
        db_session,
        conversation_id=conv.conversation_id,
        role="assistant",
        content="The manual describes setup steps.",
        input_type="text",
        citations=[citation]
    )
    assert asst_msg.message_id is not None
    assert len(asst_msg.sources) == 1
    assert asst_msg.sources[0].source_title == "User Manual"

    # Verify history
    history = DatabaseService.get_conversation_history(db_session, conv.conversation_id)
    assert len(history) == 2

    # Delete conversation
    deleted = DatabaseService.delete_conversation(db_session, conv.conversation_id)
    assert deleted is True

    # Confirm it cannot be found
    assert DatabaseService.get_conversation(db_session, conv.conversation_id) is None
