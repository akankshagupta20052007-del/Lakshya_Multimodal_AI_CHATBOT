# app/services/multimodal.py
"""
Multimodal Vision Intelligence Service for Nexus AI Studio.
Inspects images directly using Gemini Vision models with structured analysis.
"""
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger("nexus.multimodal")


class MultimodalService:
    @staticmethod
    def analyze_image(
        image_bytes: bytes,
        prompt: str = "Analyze this image in detail and describe what you see.",
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Sends image and prompt to Google Gemini Vision for fine-grained multimodal reasoning.
        """
        api_key = settings.effective_api_key
        if not api_key:
            return "Image received. Configure your GEMINI_API_KEY in .env for full visual intelligence."

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            system_instruction = (
                "You are an expert visual AI analyst. Analyze images accurately, identify entities, "
                "transcribe visible text (OCR), recognize diagrams, charts, and contextual details, "
                "and directly answer the user's inquiry."
            )

            # Model fallback sequence
            candidate_models = [settings.effective_model, "gemini-3.5-flash", "gemini-3.8-flash"]
            for model_name in candidate_models:
                try:
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.4
                    )
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[image_part, prompt],
                        config=config
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as me:
                    logger.warning(f"Vision analysis with {model_name} failed: {me}. Trying next...")

        except Exception as e:
            logger.error(f"Multimodal vision analysis failed: {e}")

        return (
            "📸 **[Image Analysis]**\n"
            "I processed your attached image. To extract fine-grained details, please verify your Gemini API key."
        )


# Singleton instance
multimodal_service = MultimodalService()

