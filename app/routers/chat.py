# app/routers/chat.py
import base64
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.chat import ChatRequest, ChatResponse, CitationSchema
from ..services.db_service import DatabaseService
from ..services.rag_service import rag_service
from ..services.llm_service import llm_service
from ..config import settings

logger = logging.getLogger("multimodal_chatbot.chat")
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def send_chat_message(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    # 1. Resolve or create conversation
    conv_id = payload.conversation_id
    is_new_conv = False
    title = payload.prompt[:40] + ("..." if len(payload.prompt) > 40 else "")
    if not conv_id:
        conv = DatabaseService.create_conversation(db, title=title)
        conv_id = conv.conversation_id
        is_new_conv = True
    else:
        conv = DatabaseService.get_conversation(db, conv_id)
        if not conv:
            # If conversation was deleted or does not exist, start a clean new chat without past memory
            conv = DatabaseService.create_conversation(db, title=title)
            conv_id = conv.conversation_id
            is_new_conv = True

    # 2. Decode multimodal payloads if present
    image_bytes = None
    if payload.image_data_base64:
        try:
            image_bytes = base64.b64decode(payload.image_data_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 encoding for image: {e}"
            )

    audio_bytes = None
    if payload.audio_data_base64:
        try:
            audio_bytes = base64.b64decode(payload.audio_data_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 encoding for audio: {e}"
            )

    # 3. Retrieve RAG context if enabled
    rag_chunks = []
    if payload.enable_rag:
        try:
            rag_chunks = rag_service.retrieve_context(
                query=payload.prompt,
                top_k=settings.TOP_K_CHUNKS
            )
        except Exception as e:
            logger.warning(f"RAG retrieval encountered an issue: {e}")

    # 4. Fetch conversation history (empty if new conversation)
    history = [] if is_new_conv else DatabaseService.get_conversation_history(db, conv_id, limit=10)

    # 5. Generate LLM response
    response_text, citations, determined_input_type, generated_image_url = llm_service.generate_response(
        prompt=payload.prompt,
        history=history,
        rag_chunks=rag_chunks,
        image_bytes=image_bytes,
        image_mime=payload.image_mime_type or "image/jpeg",
        audio_bytes=audio_bytes,
        audio_mime=payload.audio_mime_type or "audio/mp3",
    )

    # 6. Persist user message
    user_msg = DatabaseService.add_message(
        db=db,
        conversation_id=conv_id,
        role="user",
        content=payload.prompt,
        input_type=determined_input_type,
    )

    # 7. Persist assistant message with citations and optional media
    assistant_msg = DatabaseService.add_message(
        db=db,
        conversation_id=conv_id,
        role="assistant",
        content=response_text,
        input_type=determined_input_type,
        citations=citations,
        media_url=generated_image_url,
    )

    return ChatResponse(
        conversation_id=conv_id,
        user_message_id=user_msg.message_id,
        assistant_message_id=assistant_msg.message_id,
        response=response_text,
        input_type=determined_input_type,
        citations=citations,
        created_at=assistant_msg.created_at,
        generated_image_url=generated_image_url,
    )


@router.post("/multimodal", response_model=ChatResponse)
async def chat_multimodal_upload(
    prompt: str = Form(...),
    conversation_id: Optional[int] = Form(None),
    enable_rag: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Multipart/form-data endpoint to accept a prompt alongside direct file upload (image or audio).
    """
    image_bytes = None
    audio_bytes = None
    image_mime = "image/jpeg"
    audio_mime = "audio/mp3"

    if file:
        content_type = file.content_type or ""
        file_bytes = await file.read()

        if "image" in content_type:
            image_bytes = file_bytes
            image_mime = content_type
        elif "audio" in content_type:
            audio_bytes = file_bytes
            audio_mime = content_type
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported media file type: {content_type}. Upload image or audio."
            )

    req = ChatRequest(
        conversation_id=conversation_id,
        prompt=prompt,
        enable_rag=enable_rag,
    )

    # Resolve conversation
    conv_id = req.conversation_id
    is_new_conv = False
    title = prompt[:40] + ("..." if len(prompt) > 40 else "")
    if not conv_id:
        conv = DatabaseService.create_conversation(db, title=title)
        conv_id = conv.conversation_id
        is_new_conv = True
    else:
        conv = DatabaseService.get_conversation(db, conv_id)
        if not conv:
            # If conversation was deleted or not found, start clean new chat
            conv = DatabaseService.create_conversation(db, title=title)
            conv_id = conv.conversation_id
            is_new_conv = True

    rag_chunks = []
    if enable_rag:
        try:
            rag_chunks = rag_service.retrieve_context(prompt, top_k=settings.TOP_K_CHUNKS)
        except Exception as e:
            logger.warning(f"RAG retrieval error: {e}")

    history = [] if is_new_conv else DatabaseService.get_conversation_history(db, conv_id, limit=10)

    response_text, citations, determined_input_type, generated_image_url = llm_service.generate_response(
        prompt=prompt,
        history=history,
        rag_chunks=rag_chunks,
        image_bytes=image_bytes,
        image_mime=image_mime,
        audio_bytes=audio_bytes,
        audio_mime=audio_mime,
    )

    user_msg = DatabaseService.add_message(
        db=db,
        conversation_id=conv_id,
        role="user",
        content=prompt,
        input_type=determined_input_type,
    )

    assistant_msg = DatabaseService.add_message(
        db=db,
        conversation_id=conv_id,
        role="assistant",
        content=response_text,
        input_type=determined_input_type,
        citations=citations,
        media_url=generated_image_url,
    )

    return ChatResponse(
        conversation_id=conv_id,
        user_message_id=user_msg.message_id,
        assistant_message_id=assistant_msg.message_id,
        response=response_text,
        input_type=determined_input_type,
        citations=citations,
        created_at=assistant_msg.created_at,
        generated_image_url=generated_image_url,
    )
