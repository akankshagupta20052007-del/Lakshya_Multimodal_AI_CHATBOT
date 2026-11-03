# app/schemas/chat.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CitationSchema(BaseModel):
    document_id: Optional[int] = None
    source_title: Optional[str] = None
    chunk_reference: Optional[str] = None
    snippet: Optional[str] = None
    score: Optional[float] = None


class MessageCreate(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Text content of the message")
    input_type: str = Field("text", description="One of: text, image, audio, document")


class MessageResponse(BaseModel):
    message_id: int
    conversation_id: int
    role: str
    content: str
    input_type: str
    created_at: datetime
    sources: List[CitationSchema] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    title: Optional[str] = Field("New Conversation", max_length=255)


class ConversationResponse(BaseModel):
    conversation_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(BaseModel):
    conversation_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = Field(
        None,
        description="ID of existing conversation; if None, a new conversation will be created."
    )
    prompt: str = Field(..., min_length=1, description="User prompt or question")
    enable_rag: bool = Field(True, description="Whether to retrieve context from indexed documents")
    image_data_base64: Optional[str] = Field(
        None,
        description="Optional base64-encoded image string for vision questions"
    )
    image_mime_type: Optional[str] = Field("image/jpeg", description="MIME type for image")
    audio_data_base64: Optional[str] = Field(
        None,
        description="Optional base64-encoded audio string"
    )
    audio_mime_type: Optional[str] = Field("audio/mp3", description="MIME type for audio")


class ChatResponse(BaseModel):
    conversation_id: int
    user_message_id: int
    assistant_message_id: int
    response: str
    input_type: str
    citations: List[CitationSchema] = []
    created_at: datetime
    generated_image_url: Optional[str] = None
    audio_base64: Optional[str] = None
