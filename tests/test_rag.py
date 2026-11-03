# tests/test_rag.py
import pytest
import tempfile
from pathlib import Path
from app.services.rag_service import RAGService, VectorStore


def test_chunking():
    rag = RAGService()
    sample_text = (
        "Antigravity AI is an advanced agentic system. "
        "It supports multi-turn conversations, RAG document grounding, and multimodal reasoning. "
    ) * 10
    chunks = rag.chunk_text(sample_text, chunk_size=200, overlap=40)
    assert len(chunks) > 1
    for ch in chunks:
        assert len(ch) > 0


def test_vector_store_indexing_and_search():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir, dimension=128)

        # Index chunks
        doc_chunks = [
            {
                "chunk_id": "doc1_1",
                "document_id": 1,
                "document_title": "architecture.txt",
                "chunk_index": 1,
                "text": "The FastAPI backend orchestrates all requests and connects to MySQL."
            },
            {
                "chunk_id": "doc2_1",
                "document_id": 2,
                "document_title": "frontend.txt",
                "chunk_index": 1,
                "text": "The Streamlit UI provides rich chat interfaces with multimodal uploads."
            }
        ]
        store.add_chunks(doc_chunks)
        assert len(store.chunks) == 2

        # Search for backend query
        results = store.search("FastAPI and MySQL backend", top_k=2, threshold=0.01)
        assert len(results) > 0
        assert results[0].document_title == "architecture.txt"

        # Search for UI query
        ui_results = store.search("Streamlit interface", top_k=2, threshold=0.01)
        assert len(ui_results) > 0
        assert ui_results[0].document_title == "frontend.txt"

        # Test document deletion
        store.remove_by_document(1)
        assert len(store.chunks) == 1
        assert store.chunks[0]["document_id"] == 2
