# app/routers/media.py
"""
Media processing endpoints: Speech-to-Text, Text-to-Speech, and Image Generation.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from ..services.speech import speech_service
from ..services.image_gen import image_gen_service
from ..services.safety import safety_service
from ..config import settings

router = APIRouter(prefix="/media", tags=["Media Processing"])


class TextToSpeechRequest(BaseModel):
    text: str


class ImageGenRequest(BaseModel):
    prompt: str


@router.post("/speak")
def generate_speech_audio(payload: TextToSpeechRequest):
    """Converts text response to natural neural MP3 voice audio."""
    file_path, relative_url, audio_bytes = speech_service.synthesize_speech_sync(payload.text)
    if not file_path or not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synthesize speech."
        )
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename="speech.mp3",
        headers={"X-Audio-URL": relative_url}
    )


@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile = File(...)):
    """Transcribes uploaded spoken audio into text via Gemini."""
    audio_bytes = await file.read()
    valid, err = safety_service.validate_upload(
        filename=file.filename or "audio.wav",
        file_bytes=audio_bytes,
        allowed_types=["wav", "mp3", "m4a", "ogg"]
    )
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    text = speech_service.transcribe_audio(
        audio_bytes=audio_bytes,
        mime_type=file.content_type or "audio/wav"
    )
    return JSONResponse({
        "status": "success",
        "transcription": text
    })


@router.post("/generate-image")
def generate_image_endpoint(payload: ImageGenRequest):
    """Synthesizes a prompt-adherent image and saves locally."""
    file_path, relative_url, status_msg = image_gen_service.generate_image(payload.prompt)
    if not file_path:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"status": "busy", "message": status_msg}
        )
    return JSONResponse({
        "status": "success",
        "file_path": file_path,
        "image_url": relative_url,
        "message": status_msg
    })
