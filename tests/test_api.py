# tests/test_api.py
import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database_backend" in data
    assert "llm_model" in data


def test_conversation_endpoints():
    # 1. Create conversation
    res = client.post("/api/conversations", json={"title": "API Test Conv"})
    assert res.status_code == 201
    conv = res.json()
    conv_id = conv["conversation_id"]
    assert conv["title"] == "API Test Conv"

    # 2. List conversations
    res = client.get("/api/conversations")
    assert res.status_code == 200
    items = res.json()
    assert any(c["conversation_id"] == conv_id for c in items)

    # 3. Get detail
    res = client.get(f"/api/conversations/{conv_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["conversation_id"] == conv_id
    assert isinstance(detail["messages"], list)

    # 4. Delete
    del_res = client.delete(f"/api/conversations/{conv_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True


def test_chat_endpoint():
    # Send text chat message
    chat_payload = {
        "prompt": "Hello assistant, how does multimodal RAG work?",
        "enable_rag": True
    }
    res = client.post("/api/chat", json=chat_payload)
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "conversation_id" in data
    assert data["user_message_id"] > 0
    assert data["assistant_message_id"] > 0


def test_document_upload_and_list():
    sample_content = b"Multimodal Chatbot Specification. It handles text, PDFs, images, and audio."
    file = io.BytesIO(sample_content)

    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("spec.txt", file, "text/plain")}
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    assert doc_data["filename"] == "spec.txt"
    assert doc_data["chunks_indexed"] >= 1
    doc_id = doc_data["document_id"]

    # Verify listing
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert any(d["document_id"] == doc_id for d in docs)

    # Clean up
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200
