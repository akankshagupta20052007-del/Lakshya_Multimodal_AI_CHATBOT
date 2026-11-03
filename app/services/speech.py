# app/services/speech.py
"""
Speech-to-Text (STT) and Text-to-Speech (TTS) Voice Engine.
- STT: Transcribes spoken microphone/audio recordings using Gemini's native audio capabilities.
- TTS: Zero extra API key required. Converts text to speech using edge-tts with gTTS fallback.
- Saves audio to ./data/generated/audio/ with local playback and download support.
"""
import re
import io
import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional
from ..config import settings

logger = logging.getLogger("nexus.speech")


class SpeechService:
    def __init__(self):
        self.output_dir = settings.resolved_audio_dir

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        """
        Transcribes spoken audio using Gemini's native audio understanding.
        Uses single centralized GEMINI_API_KEY.
        """
        api_key = settings.effective_api_key
        if not api_key:
            return "Audio received (Gemini API key not configured)."

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

            prompt = (
                "Accurately transcribe the spoken words in this audio into clear text. "
                "Output only the verbatim transcription without commentary."
            )

            # Try primary model then fallback
            for model_name in [settings.effective_model, "gemini-3.5-flash", "gemini-3.8-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[audio_part, prompt]
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as me:
                    logger.warning(f"Audio transcription with {model_name} failed: {me}")

        except Exception as e:
            logger.error(f"Speech transcription failed: {e}")

        return "Could not transcribe audio recording."

    @staticmethod
    def clean_text_for_speech(text: str) -> str:
        """Removes markdown symbols, URLs, and asterisks for smooth, natural audio readout."""
        # Strip code blocks
        clean = re.sub(r'```[\s\S]*?```', '', text)
        # Strip inline code
        clean = re.sub(r'`[^`]*`', '', clean)
        # Strip URLs
        clean = re.sub(r'https?://\S+', '', clean)
        # Strip markdown syntax symbols
        clean = re.sub(r'[*_#~>\[\]\(\)]', ' ', clean)
        # Collapse multiple whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        # Cap length to avoid excessive synthesis delays
        if len(clean) > 800:
            clean = clean[:797] + "..."
        return clean

    def synthesize_speech_sync(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[bytes]]:
        """
        Synchronous wrapper around text-to-speech synthesis.
        Returns: (file_path, relative_url, raw_bytes)
        """
        clean_text = self.clean_text_for_speech(text)
        if not clean_text:
            return None, None, None

        filename = f"voice_{uuid.uuid4().hex[:12]}.mp3"
        file_path = self.output_dir / filename
        relative_url = f"/static/audio/{filename}"

        # 1. Try edge-tts for high-quality natural neural voice
        try:
            import edge_tts

            async def _synthesize():
                comm = edge_tts.Communicate(clean_text, voice="en-US-AriaNeural")
                await comm.save(str(file_path))

            # Run in event loop safely
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(asyncio.run, _synthesize()).result()
            else:
                asyncio.run(_synthesize())

            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, "rb") as f:
                    data = f.read()
                return str(file_path), relative_url, data

        except Exception as e:
            logger.warning(f"edge-tts failed: {e}. Falling back to gTTS.")

        # 2. Fallback to gTTS (Google Text-to-Speech)
        try:
            from gtts import gTTS
            tts = gTTS(text=clean_text, lang='en')
            tts.save(str(file_path))

            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, "rb") as f:
                    data = f.read()
                return str(file_path), relative_url, data
        except Exception as ge:
            logger.error(f"gTTS fallback also failed: {ge}")

        return None, None, None


# Singleton instance
speech_service = SpeechService()
