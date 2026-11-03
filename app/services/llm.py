# app/services/llm.py
"""
Central LLM & Empathy Engine for Nexus Multimodal AI Studio.
- Uses official google-genai SDK with single GEMINI_API_KEY.
- Primary model: gemini-3.5-flash-lite with dynamic fallback chain (gemini-3.5-flash, gemini-3.8-flash).
- Empathetic System Prompt for stress, burnout, and academic pressure.
- Priority Safety: Bypasses LLM and returns 988 Lifeline on self-harm detection.
- Contextual Grounding with RAG & Multimodal input handling.
"""
import logging
from typing import List, Optional, Tuple
from ..config import settings
from ..schemas.chat import CitationSchema
from ..schemas.document import DocumentChunk
from ..models import Message
from .safety import safety_service
from .image_gen import image_gen_service

logger = logging.getLogger("nexus.llm")

# Empathetic system instructions
LAKSHYA_SYSTEM_INSTRUCTION = (
    "You are Lakshya, an intelligent, empathetic, supportive, and professional multimodal AI assistant. "
    "You provide structured, compassionate, and practical advice for productivity, stress, burnout, and technical inquiries. "
    "You listen attentively, validate the user's emotional state, and suggest clear, actionable solutions. "
    "You never claim to be human, and you never give medical, clinical, or psychiatric diagnoses. "
    "Ground your answers thoroughly using retrieved document context when provided, citing the document title. "
    "If an image or audio is provided, analyze it accurately and integrate it into your response."
)


class LLMService:
    def __init__(self):
        self._cached_client = None
        self._cached_api_key = None

    def _get_client(self, api_key: str):
        """Maintains a persistent client for TLS reuse and low latency."""
        if self._cached_client is None or self._cached_api_key != api_key:
            from google import genai
            self._cached_client = genai.Client(api_key=api_key)
            self._cached_api_key = api_key
        return self._cached_client

    def _generate_mock_response(
        self,
        prompt: str,
        input_type: str,
        rag_chunks: List[DocumentChunk]
    ) -> str:
        """Contextual fallback for offline or unauthenticated testing."""
        parts = []
        if rag_chunks:
            parts.append(
                "📚 **Grounded Information from Documents:**\n"
                f"Based on `{len(rag_chunks)}` retrieved knowledge source(s):\n"
            )
            for idx, ch in enumerate(rag_chunks, 1):
                snippet = ch.text.replace("\n", " ").strip()
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                parts.append(f"> **[{idx}] {ch.document_title}** ({ch.chunk_id}):\n> *\"{snippet}\"*\n")
            parts.append(f"\nIn response to *\"{prompt}\"*, the documentation covers the relevant requirements.")
        else:
            parts.append(
                f"Hello! I am Lakshya, your Multimodal AI Studio assistant. "
                f"I received your inquiry: \"{prompt}\".\n\n"
                "I can analyze images, transcribe voice recordings, search reference documents with citations, "
                "or generate prompt-adherent images."
            )
        return "\n\n".join(parts)

    def generate_response(
        self,
        prompt: str,
        history: Optional[List[Message]] = None,
        rag_chunks: Optional[List[DocumentChunk]] = None,
        image_bytes: Optional[bytes] = None,
        image_mime: str = "image/jpeg",
        audio_bytes: Optional[bytes] = None,
        audio_mime: str = "audio/mp3",
    ) -> Tuple[str, List[CitationSchema], str, Optional[str]]:
        """
        Generates response across text, empathy, multimodal vision/audio, or image generation.
        Returns: (response_text, citations, determined_input_type, generated_image_url)
        """
        # 1. PRIORITY SAFETY CHECK (988 Lifeline Bypass)
        is_crisis, crisis_message = safety_service.check_crisis(prompt)
        if is_crisis:
            logger.warning("Priority Safety triggered: Crisis Lifeline activated.")
            return crisis_message, [], "crisis_intervention", None

        # 2. IMAGE GENERATION CHECK
        if not image_bytes and not audio_bytes and not rag_chunks and image_gen_service.is_image_request(prompt):
            img_path, img_url, status_msg = image_gen_service.generate_image(prompt)
            if img_path:
                return status_msg, [], "image_generation", img_url or img_path
            else:
                return status_msg, [], "text", None

        # 3. Determine input type
        rag_chunks = rag_chunks or []
        citations: List[CitationSchema] = []
        if image_bytes:
            input_type = "image"
        elif audio_bytes:
            input_type = "audio"
        elif rag_chunks:
            input_type = "document"
        else:
            input_type = "text"

        # Build citations
        for ch in rag_chunks:
            citations.append(CitationSchema(
                document_id=ch.document_id,
                source_title=ch.document_title,
                chunk_reference=ch.chunk_id,
                snippet=ch.text[:350] + ("..." if len(ch.text) > 350 else ""),
                score=ch.score
            ))

        # 4. GOOGLE GEMINI EXECUTION
        api_key = settings.effective_api_key
        if api_key:
            try:
                from google.genai import types
                client = self._get_client(api_key)

                contents = []

                # Build grounded RAG context prefix
                if rag_chunks:
                    rag_context_text = "### VERIFIED DOCUMENT CONTEXT FOR CITATIONS:\n"
                    for ch in rag_chunks:
                        rag_context_text += (
                            f"\n[Source Document: '{ch.document_title}', Chunk: '{ch.chunk_id}']\n"
                            f"{ch.text}\n"
                        )
                    rag_context_text += "\n### END CONTEXT\n\n"
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=rag_context_text)]
                    ))

                # Inject conversation history turns
                if history:
                    for prev in history[-6:]:
                        role = "user" if prev.role == "user" else "model"
                        contents.append(types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=prev.content)]
                        ))

                # Build current user prompt parts
                current_parts = []
                if image_bytes:
                    current_parts.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
                if audio_bytes:
                    current_parts.append(types.Part.from_bytes(data=audio_bytes, mime_type=audio_mime))
                current_parts.append(types.Part.from_text(text=prompt))

                contents.append(types.Content(role="user", parts=current_parts))

                config = types.GenerateContentConfig(
                    system_instruction=LAKSHYA_SYSTEM_INSTRUCTION,
                    temperature=0.3 if rag_chunks else 0.7,
                )

                # Fallback chain to avoid 503 spike errors
                models_to_try = [settings.effective_model, "gemini-3.5-flash", "gemini-3.8-flash"]
                deduped_models = []
                for m in models_to_try:
                    if m and m not in deduped_models:
                        deduped_models.append(m)

                for candidate in deduped_models:
                    try:
                        response = client.models.generate_content(
                            model=candidate,
                            contents=contents,
                            config=config
                        )
                        if response and response.text:
                            return response.text, citations, input_type, None
                    except Exception as model_err:
                        logger.warning(f"Generation with {candidate} failed: {model_err}. Trying fallback model...")

            except Exception as e:
                logger.error(f"Gemini execution error: {e}")

        # 5. Offline Fallback
        mock_reply = self._generate_mock_response(prompt, input_type, rag_chunks)
        return mock_reply, citations, input_type, None


# Singleton instance
llm_service = LLMService()

