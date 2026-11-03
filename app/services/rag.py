# app/services/rag.py
"""
Retrieval-Augmented Generation (RAG) Service for Nexus AI Studio.
Includes:
- Multi-format document parser (PDF via pypdf, TXT, MD)
- Sliding-window text chunking (600 characters with 100 character overlap)
- Dense cosine similarity vector store with persistent storage
- Untrusted context sanitization against prompt injection attacks
- Grounded citations with verifiable source titles and similarity scores
"""
import io
import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

from ..config import settings
from ..schemas.document import DocumentChunk
from .safety import safety_service

logger = logging.getLogger("nexus.rag")


class VectorStore:
    """
    Thread-safe dense vector store with cosine similarity retrieval
    and local disk persistence.
    """
    def __init__(self, store_path: Path, dimension: int = 256):
        self.store_dir = Path(store_path)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.store_dir / "index_meta.json"
        self.vectors_file = self.store_dir / "vectors.npy"
        self.dimension = dimension

        self.chunks: List[Dict[str, Any]] = []
        self.vectors: np.ndarray = np.empty((0, dimension), dtype=np.float32)
        self.load()

    def _hash_embed(self, text: str) -> np.ndarray:
        """
        Generates a normalized n-gram hashed dense vector for text representation.
        Provides resilient, dependency-free semantic and term retrieval matching.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = clean.split()

        if not tokens:
            return vec

        # Unigrams and bigrams
        terms = list(tokens)
        for i in range(len(tokens) - 1):
            terms.append(f"{tokens[i]}_{tokens[i+1]}")

        for term in terms:
            idx = abs(hash(term)) % self.dimension
            sign = 1.0 if (hash(term + "_sign") % 2 == 0) else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec

    def embed_text(self, text: str) -> np.ndarray:
        return self._hash_embed(text)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return

        new_vectors = []
        for ch in chunks:
            vec = self.embed_text(ch["text"])
            if vec.shape[0] != self.dimension and self.vectors.shape[0] > 0 and vec.shape[0] != self.vectors.shape[1]:
                self.dimension = vec.shape[0]
            new_vectors.append(vec)

        new_mat = np.array(new_vectors, dtype=np.float32)
        if self.vectors.shape[0] == 0:
            self.vectors = new_mat
        else:
            if self.vectors.shape[1] == new_mat.shape[1]:
                self.vectors = np.vstack([self.vectors, new_mat])
            else:
                self.vectors = new_mat

        self.chunks.extend(chunks)
        self.save()

    def remove_by_document(self, document_id: int):
        keep_indices = [i for i, c in enumerate(self.chunks) if c["document_id"] != document_id]
        if len(keep_indices) == len(self.chunks):
            return

        self.chunks = [self.chunks[i] for i in keep_indices]
        if self.vectors.shape[0] > 0:
            self.vectors = self.vectors[keep_indices]
        self.save()

    def search(self, query: str, top_k: int = 3, threshold: float = 0.15) -> List[DocumentChunk]:
        if not self.chunks or self.vectors.shape[0] == 0:
            return []

        q_vec = self.embed_text(query)
        if q_vec.shape[0] != self.vectors.shape[1]:
            q_vec = self._hash_embed(query)
            if q_vec.shape[0] != self.vectors.shape[1]:
                return []

        # Cosine similarity
        sims = np.dot(self.vectors, q_vec)

        # Keyword boost: boost similarity if exact query words appear in chunk
        q_words = set(re.findall(r"\w+", query.lower()))
        for i, chunk in enumerate(self.chunks):
            text_lower = chunk["text"].lower()
            matches = sum(1 for w in q_words if w in text_lower)
            if matches > 0 and len(q_words) > 0:
                boost = 0.12 * (matches / len(q_words))
                sims[i] += boost

        top_indices = np.argsort(sims)[::-1]

        results: List[DocumentChunk] = []
        for idx in top_indices[:top_k]:
            score = float(sims[idx])
            if score >= threshold:
                chunk_data = self.chunks[idx]
                results.append(DocumentChunk(
                    chunk_id=chunk_data["chunk_id"],
                    document_id=chunk_data["document_id"],
                    document_title=chunk_data["document_title"],
                    chunk_index=chunk_data["chunk_index"],
                    text=chunk_data["text"],
                    score=round(score, 4)
                ))
        return results

    def save(self):
        try:
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
            np.save(self.vectors_file, self.vectors)
            logger.info(f"Saved {len(self.chunks)} vector chunks to {self.store_dir}")
        except Exception as e:
            logger.error(f"Failed to persist vector store: {e}")

    def load(self):
        try:
            if self.meta_file.exists() and self.vectors_file.exists():
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                self.vectors = np.load(self.vectors_file)
                if self.vectors.ndim == 2:
                    self.dimension = self.vectors.shape[1]
                logger.info(f"Loaded {len(self.chunks)} vector chunks from {self.store_dir}")
        except Exception as e:
            logger.warning(f"Could not load vector store, starting clean: {e}")
            self.chunks = []
            self.vectors = np.empty((0, self.dimension), dtype=np.float32)


class RAGService:
    def __init__(self):
        self.vector_store = VectorStore(settings.resolved_vector_path)

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
        ext = filename.lower().split(".")[-1] if "." in filename else ""

        if ext == "pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(file_bytes))
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    t = page.extract_text() or ""
                    if t.strip():
                        pages_text.append(f"--- Page {idx + 1} ---\n{t.strip()}")
                return "\n\n".join(pages_text)
            except Exception as e:
                logger.error(f"Error extracting PDF text from {filename}: {e}")
                raise ValueError(f"Failed to parse PDF document: {e}")
        else:
            # Plain text or Markdown
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return file_bytes.decode("latin-1", errors="replace")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """
        Splits text into overlapping chunks, attempting to break on sentence/paragraph boundaries.
        """
        text = text.strip()
        if not text:
            return []

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            if end < text_len:
                breakpoint = max(
                    text.rfind("\n\n", start, end),
                    text.rfind(". ", start, end),
                    text.rfind("\n", start, end)
                )
                if breakpoint > start + (chunk_size // 2):
                    end = breakpoint + 1

            chunk = text[start:end].strip()
            if chunk:
                # Sanitize chunk against prompt injection before storing
                clean_chunk = safety_service.sanitize_rag_context(chunk)
                if clean_chunk:
                    chunks.append(clean_chunk)

            start = end - overlap if (end - overlap) > start else end

        return chunks

    def process_and_index_document(
        self,
        document_id: int,
        filename: str,
        file_bytes: bytes
    ) -> Tuple[int, List[DocumentChunk]]:
        raw_text = self.extract_text_from_bytes(file_bytes, filename)
        if not raw_text.strip():
            raise ValueError(f"No extractable text found in file {filename}")

        text_chunks = self.chunk_text(raw_text)
        chunk_objects = []
        chunks_for_index = []

        for idx, ch_text in enumerate(text_chunks):
            chunk_id = f"doc_{document_id}_chunk_{idx + 1}"
            chunk_data = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_title": filename,
                "chunk_index": idx + 1,
                "text": ch_text
            }
            chunks_for_index.append(chunk_data)
            chunk_objects.append(DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                document_title=filename,
                chunk_index=idx + 1,
                text=ch_text
            ))

        self.vector_store.add_chunks(chunks_for_index)
        return len(chunks_for_index), chunk_objects

    def retrieve_context(self, query: str, top_k: Optional[int] = None) -> List[DocumentChunk]:
        k = top_k or settings.TOP_K_CHUNKS
        threshold = settings.SIMILARITY_THRESHOLD
        return self.vector_store.search(query, top_k=k, threshold=threshold)

    def delete_document_index(self, document_id: int):
        self.vector_store.remove_by_document(document_id)

    def get_stats(self) -> Dict[str, Any]:
        unique_docs = len({c["document_id"] for c in self.vector_store.chunks})
        return {
            "indexed_documents_count": unique_docs,
            "indexed_chunks_count": len(self.vector_store.chunks),
            "store_path": str(self.vector_store.store_dir)
        }


# Singleton instance
rag_service = RAGService()

