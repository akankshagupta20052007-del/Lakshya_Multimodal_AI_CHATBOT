# streamlit_app.py
"""
Lakshya Multimodal AI Studio — Executive Dark UI
Single API Key Architecture | Gemini-Enhanced Image Gen | Direct Chatbar Mic | Voice STT/TTS | RAG | Empathy Engine
"""
import os
import re
import time
import base64
import requests
import streamlit as st
from pathlib import Path
from typing import Optional, List, Dict, Any

# Root base directory
BASE_DIR = Path(__file__).resolve().parent

# Page Configuration
st.set_page_config(
    page_title="Lakshya Multimodal AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


# --- CSS FOR EXECUTIVE PROFESSIONAL THEME & AI CORE ---
PROFESSIONAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Global Font & Theme */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at top, #0f172a 0%, #070b14 60%, #03060a 100%) !important;
    color: #e2e8f0;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background-color: #070b14 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

/* Background animated subtle stars & nebula */
.cosmic-stars {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    background: transparent;
    overflow: hidden;
}

.star {
    position: absolute;
    width: 2px;
    height: 2px;
    background: #e0e7ff;
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(129, 140, 248, 0.8);
    animation: driftUp 16s linear infinite;
}

@keyframes driftUp {
    0% { transform: translateY(100vh); opacity: 0; }
    20% { opacity: 0.85; }
    80% { opacity: 0.85; }
    100% { transform: translateY(-10vh); opacity: 0; }
}

/* Center Hero AI Core Orb */
.hero-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2.2rem 1rem 1.2rem 1rem;
    text-align: center;
    position: relative;
    z-index: 1;
}

.core-avatar-wrapper {
    position: relative;
    width: 104px;
    height: 104px;
    margin-bottom: 1.4rem;
}

.core-outer-ring {
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 2px dashed rgba(99, 102, 241, 0.5);
    animation: spinRing 20s linear infinite;
}

@keyframes spinRing {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.core-orb {
    width: 104px;
    height: 104px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #38bdf8 0%, #6366f1 50%, #1e1b4b 100%);
    box-shadow: 0 0 35px rgba(99, 102, 241, 0.55), inset 0 0 16px rgba(255, 255, 255, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: floatOrb 4s ease-in-out infinite;
}

@keyframes floatOrb {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-10px) scale(1.02); }
}

.core-symbol {
    font-size: 2.3rem;
    color: #ffffff;
    filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #6ee7b7;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
}

.status-dot {
    width: 7px;
    height: 7px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
    animation: pulseDot 2s infinite;
}

@keyframes pulseDot {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.6; }
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #f8fafc 0%, #c7d2fe 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    max-width: 660px;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

/* Chat Message Cards */
[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    margin-bottom: 1rem !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3) !important;
}

/* Mode & Attachment Badges */
.mode-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99, 102, 241, 0.18);
    border: 1px solid rgba(99, 102, 241, 0.45);
    color: #c7d2fe;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 8px;
}

.attachment-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.16);
    border: 1px solid rgba(56, 189, 248, 0.45);
    color: #bae6fd;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 8px;
}

/* Crisis Intervention Banner */
.crisis-box {
    background: rgba(220, 38, 38, 0.16);
    border: 1px solid #ef4444;
    border-radius: 14px;
    padding: 1.2rem;
    color: #fee2e2;
    margin-bottom: 1rem;
    box-shadow: 0 0 25px rgba(239, 68, 68, 0.2);
}

/* Modern Pill Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
}

button[kind="secondary"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    background: rgba(255, 255, 255, 0.04) !important;
    color: #f1f5f9 !important;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}
</style>
<div class="cosmic-stars">
    <div class="star" style="left: 12%; animation-delay: 0s;"></div>
    <div class="star" style="left: 28%; animation-delay: 4s;"></div>
    <div class="star" style="left: 45%; animation-delay: 8s;"></div>
    <div class="star" style="left: 62%; animation-delay: 2s;"></div>
    <div class="star" style="left: 78%; animation-delay: 11s;"></div>
    <div class="star" style="left: 90%; animation-delay: 6s;"></div>
</div>
"""
st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)


# --- API CLIENT HELPERS ---
def api_get_health() -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_list_conversations() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE_URL}/api/conversations", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def api_get_conversation(conv_id: int) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE_URL}/api/conversations/{conv_id}", timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_delete_conversation(conv_id: int) -> bool:
    try:
        r = requests.delete(f"{API_BASE_URL}/api/conversations/{conv_id}", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


def api_list_documents() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE_URL}/api/documents", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def api_delete_document(doc_id: int) -> bool:
    try:
        r = requests.delete(f"{API_BASE_URL}/api/documents/{doc_id}", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


def api_upload_document(filename: str, content_bytes: bytes) -> Optional[Dict[str, Any]]:
    try:
        files = {"file": (filename, content_bytes, "application/octet-stream")}
        r = requests.post(f"{API_BASE_URL}/api/documents/upload", files=files, timeout=30)
        if r.status_code == 201:
            return r.json()
        else:
            st.error(f"Document upload error ({r.status_code}): {r.text}")
    except Exception as e:
        st.error(f"Upload connection error: {e}")
    return None


def api_transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Transcribes spoken voice into text using Gemini audio understanding."""
    try:
        files = {"file": ("mic_recording.wav", audio_bytes, mime_type)}
        r = requests.post(f"{API_BASE_URL}/api/media/transcribe", files=files, timeout=25)
        if r.status_code == 200:
            return r.json().get("transcription", "")
    except Exception:
        pass
    try:
        from app.services.speech import speech_service
        return speech_service.transcribe_audio(audio_bytes, mime_type)
    except Exception:
        return "Could not transcribe audio recording."


def api_send_chat(
    prompt: str,
    conv_id: Optional[int],
    enable_rag: bool,
    image_bytes: Optional[bytes] = None,
    image_mime: str = "image/jpeg",
    audio_bytes: Optional[bytes] = None,
    audio_mime: str = "audio/wav",
) -> Optional[Dict[str, Any]]:
    try:
        payload = {
            "prompt": prompt,
            "conversation_id": conv_id,
            "enable_rag": enable_rag,
        }
        if image_bytes:
            payload["image_data_base64"] = base64.b64encode(image_bytes).decode("utf-8")
            payload["image_mime_type"] = image_mime
        if audio_bytes:
            payload["audio_data_base64"] = base64.b64encode(audio_bytes).decode("utf-8")
            payload["audio_mime_type"] = audio_mime

        r = requests.post(f"{API_BASE_URL}/api/chat", json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Chat request failed ({r.status_code}): {r.text}")
    except Exception as e:
        st.error(f"Backend connection error: {e}")
    return None


def api_synthesize_speech(text: str) -> Optional[bytes]:
    """Requests TTS voice synthesis from zero-key voice service."""
    try:
        clean_text = re.sub(r'[*_#`>\[\]\(\)]', ' ', text)
        clean_text = re.sub(r'https?://\S+', '', clean_text).strip()
        if not clean_text:
            return None
        r = requests.post(f"{API_BASE_URL}/api/media/speak", json={"text": clean_text[:600]}, timeout=25)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    try:
        from gtts import gTTS
        import io
        clean_text = re.sub(r'[*_#`>\[\]\(\)]', ' ', text)[:500].strip()
        tts = gTTS(text=clean_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return None


# --- SESSION STATE INITIALIZATION ---
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_cache" not in st.session_state:
    st.session_state.audio_cache = {}
if "active_mode" not in st.session_state:
    st.session_state.active_mode = None
if "attached_file" not in st.session_state:
    st.session_state.attached_file = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None
if "mic_seed" not in st.session_state:
    st.session_state.mic_seed = 0
if "last_processed_audio_bytes" not in st.session_state:
    st.session_state.last_processed_audio_bytes = None


def start_new_chat():
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.session_state.audio_cache = {}
    st.session_state.active_mode = None
    st.session_state.attached_file = None
    st.session_state.pending_prompt = None
    st.session_state.mic_seed += 1
    st.session_state.last_processed_audio_bytes = None


def load_past_chat(conv_id: int):
    st.session_state.current_conversation_id = conv_id
    detail = api_get_conversation(conv_id)
    if detail and "messages" in detail:
        st.session_state.messages = detail["messages"]
    else:
        st.session_state.messages = []
    st.session_state.audio_cache = {}
    st.session_state.active_mode = None
    st.session_state.attached_file = None
    st.session_state.pending_prompt = None


# --- SIDEBAR (Conversations, Knowledge Base, System Status) ---
with st.sidebar:
    st.markdown("### ⚡ Lakshya AI")
    st.caption("Multimodal Intelligence Studio • Google Gemini 3.5")

    health = api_get_health()
    if health:
        backend_color = "🟢" if health.get("status") == "healthy" else "🟡"
        st.success(
            f"{backend_color} **Studio Active**\n\n"
            f"• **Core Engine:** `{health.get('llm_model')}`\n\n"
            f"• **Storage:** `{health.get('database_backend')}`\n\n"
            f"• **Knowledge Index:** `{health.get('indexed_chunks_count')}` chunks"
        )
    else:
        st.error("🔴 **Studio Offline**\n\nRun `start.bat` or `uvicorn app.main:app`")

    st.markdown("---")
    if st.button("➕ Start New Session", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()

    enable_rag = st.checkbox("🔍 Ground Answers with Knowledge Base (RAG)", value=True)
    auto_speak = st.checkbox("🔊 Auto-speak Assistant Responses", value=False)

    st.markdown("---")
    st.markdown("#### 💬 Past Sessions")
    conversations = api_list_conversations()
    if conversations:
        for c in conversations:
            c_id = c["conversation_id"]
            is_active = (c_id == st.session_state.current_conversation_id)
            col1, col2 = st.columns([0.82, 0.18])
            label = f"{'▶ ' if is_active else ''}{c.get('title', f'Chat {c_id}')}"
            if col1.button(label, key=f"conv_btn_{c_id}", use_container_width=True):
                load_past_chat(c_id)
                st.rerun()
            if col2.button("🗑️", key=f"del_btn_{c_id}", help="Delete chat completely"):
                api_delete_conversation(c_id)
                if st.session_state.current_conversation_id == c_id:
                    start_new_chat()
                st.rerun()
    else:
        st.caption("No previous sessions recorded.")

    st.markdown("---")
    st.markdown("#### 📚 Knowledge Base Index")
    docs = api_list_documents()
    if docs:
        for d in docs:
            d_id = d["document_id"]
            d_col1, d_col2 = st.columns([0.82, 0.18])
            d_col1.write(f"📄 `{d['filename']}`")
            if d_col2.button("❌", key=f"del_doc_{d_id}", help="Remove from index"):
                api_delete_document(d_id)
                st.rerun()
    else:
        st.caption("No documents in Knowledge Base. Attach files via [ ＋ Studio Tools ▾ ].")

    st.markdown("---")
    st.markdown("#### 🎓 Project Documentation")
    report_path = BASE_DIR / "data" / "generated" / "docs" / "Lakshya_Project_Report.pdf"
    if not report_path.exists():
        report_path = BASE_DIR / "Lakshya_Project_Report.pdf"
    if report_path.exists():
        with open(report_path, "rb") as rf:
            report_bytes = rf.read()
        st.download_button(
            label="📥 Download Project Report (PDF)",
            data=report_bytes,
            file_name="Lakshya_Project_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Download complete 6-page academic project report by Akanksha Gupta"
        )


# --- HERO SCREEN (Shown when conversation is empty) ---
if len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div class="hero-container">
            <div class="core-avatar-wrapper">
                <div class="core-outer-ring"></div>
                <div class="core-orb">
                    <span class="core-symbol">⚡</span>
                </div>
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                Lakshya V3.5 Active • Vision • Voice • RAG • Art
            </div>
            <div class="hero-title">Lakshya Multimodal AI Studio</div>
            <div class="hero-subtitle">
                Autonomous multimodal intelligence powered by Google Gemini. Converse naturally via voice, 
                inspect vision data, search knowledge repositories, and synthesize creative artwork.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4 Professional Action Cards
    chip_cols = st.columns(4)
    with chip_cols[0]:
        if st.button("🎨 Create Cyberpunk City", use_container_width=True):
            st.session_state.pending_prompt = "Generate an image of a vibrant cyberpunk city at night with neon reflections in rain"
            st.rerun()
    with chip_cols[1]:
        if st.button("🧠 Stress & Focus Coaching", use_container_width=True):
            st.session_state.pending_prompt = "I've been feeling stressed and burned out with heavy deadlines lately. Can you help me reset?"
            st.rerun()
    with chip_cols[2]:
        if st.button("🌿 4-7-8 Breathing Reset", use_container_width=True):
            st.session_state.pending_prompt = "Please guide me through a soothing 4-7-8 breathing and relaxation reset."
            st.rerun()
    with chip_cols[3]:
        if st.button("📚 Search Knowledge Base", use_container_width=True):
            st.session_state.pending_prompt = "What stress management and productivity advice is covered in the documentation?"
            st.rerun()


# --- DISPLAY CHAT FEED ---
for idx, msg in enumerate(st.session_state.messages):
    role = msg.get("role", "user")
    content = msg.get("content", "")
    citations = msg.get("sources", []) or []
    input_type = msg.get("input_type", "text")
    msg_id = msg.get("message_id", idx)
    avatar = "👤" if role == "user" else "⚡"

    with st.chat_message(role, avatar=avatar):
        # Multimodal Badge
        if input_type and input_type not in ["text"] and role == "user":
            type_label = {
                "image": "🖼️ Image Query",
                "audio": "🎙️ Voice Query",
                "document": "📄 Document Query",
                "image_generation": "🎨 Image Generation",
                "crisis_intervention": "💙 Crisis Support"
            }.get(input_type, input_type)
            st.caption(f"**Format:** `{type_label}`")

        # Special styling for crisis intervention
        if input_type == "crisis_intervention" or "988" in content:
            st.markdown(f'<div class="crisis-box">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(content)

        # Display Generated Image if present
        media_url = msg.get("media_url") or msg.get("generated_image_url")
        if media_url:
            img_file_path = None
            if media_url.startswith("/static/images/"):
                img_name = media_url.replace("/static/images/", "")
                potential_path = BASE_DIR / "data" / "generated" / "images" / img_name
                if potential_path.exists():
                    img_file_path = potential_path

            if img_file_path and img_file_path.exists():
                st.image(str(img_file_path), caption="Lakshya Generated Artwork", use_container_width=True)
                with open(img_file_path, "rb") as f:
                    img_data = f.read()
                st.download_button(
                    label="⬇️ Download High-Res Artwork",
                    data=img_data,
                    file_name=f"lakshya_{msg_id}.jpg",
                    mime="image/jpeg",
                    key=f"dl_img_{msg_id}"
                )
            elif media_url.startswith("http"):
                st.image(media_url, caption="Lakshya Generated Artwork", use_container_width=True)

        # Show RAG Citations
        if citations:
            with st.expander(f"📚 Verified Citations & References ({len(citations)})", expanded=False):
                for cite_idx, cite in enumerate(citations, 1):
                    title = cite.get("source_title", "Document")
                    chunk_id = cite.get("chunk_reference", "")
                    score = cite.get("score")
                    score_str = f" • Similarity: `{score:.2f}`" if score is not None else ""
                    st.markdown(f"**[{cite_idx}] {title}** ({chunk_id}){score_str}")
                    st.info(f"\"{cite.get('snippet', '')}\"")

        # Voice Playback for Assistant Responses
        if role == "assistant":
            cached_audio = st.session_state.audio_cache.get(msg_id)
            if cached_audio:
                st.audio(cached_audio, format="audio/mp3")
            else:
                speak_col, _ = st.columns([0.24, 0.76])
                if speak_col.button("🔊 Listen to Voice", key=f"speak_btn_{msg_id}"):
                    with st.spinner("Synthesizing neural voice..."):
                        audio_data = api_synthesize_speech(content)
                        if audio_data:
                            st.session_state.audio_cache[msg_id] = audio_data
                            st.rerun()


# --- CONTROLS DOCK (Placed Directly Above the Unified Chat Bar) ---
dock_col1, dock_col2 = st.columns([0.22, 0.78])

with dock_col1:
    with st.popover("＋ Studio Tools ▾", use_container_width=True):
        st.markdown("**⚡ Lakshya Tools**")

        # Action 1: 🎨 Image Generation
        if st.button("🎨 Creative Image Mode", use_container_width=True):
            st.session_state.active_mode = "image"
            st.rerun()

        # Action 2: 📎 File Upload
        with st.expander("📎 Attach File (Vision, Voice, Docs)"):
            up_file = st.file_uploader(
                "Upload File",
                type=["png", "jpg", "jpeg", "webp", "wav", "mp3", "m4a", "pdf", "txt", "md"],
                key="dock_file_uploader"
            )
            if up_file:
                file_bytes = up_file.getvalue()
                ext = up_file.name.lower().split(".")[-1]
                mime = up_file.type or "application/octet-stream"

                # If PDF/TXT/MD, allow direct index into Knowledge Base
                if ext in ["pdf", "txt", "md"]:
                    if st.button("📥 Index into Knowledge Base", use_container_width=True, type="primary"):
                        with st.spinner(f"Indexing '{up_file.name}' into RAG vector repository..."):
                            res = api_upload_document(up_file.name, file_bytes)
                            if res:
                                st.success(f"Indexed {res.get('chunks_indexed', 1)} chunks from '{up_file.name}'!")
                                time.sleep(1)
                                st.rerun()

                st.session_state.attached_file = {
                    "name": up_file.name,
                    "bytes": file_bytes,
                    "mime": mime,
                    "ext": ext
                }
                st.success(f"Attached: {up_file.name}")

        # Action 3: 🧠 Emotional Support
        if st.button("🧠 Wellness & Empathy", use_container_width=True):
            st.session_state.active_mode = "empathy"
            st.rerun()

        # Action 4: 🌿 Relax & Chill
        if st.button("🌿 Mindful Reset", use_container_width=True):
            st.session_state.pending_prompt = "Please guide me through a soothing, mindful relaxation and breathing reset."
            st.rerun()

with dock_col2:
    # Direct Inline Microphone Recorder right at the chat bar
    mic_audio = st.audio_input(
        "🎙️ Click to speak / record audio",
        key=f"chatbar_mic_{st.session_state.mic_seed}",
        label_visibility="collapsed"
    )


# --- HANDLE DIRECT VOICE RECORDING FROM CHATBAR ---
if mic_audio is not None:
    raw_audio_bytes = mic_audio.getvalue()
    if raw_audio_bytes and raw_audio_bytes != st.session_state.last_processed_audio_bytes:
        st.session_state.last_processed_audio_bytes = raw_audio_bytes
        with st.spinner("🎙️ Listening & transcribing your voice..."):
            transcribed_speech = api_transcribe_audio(raw_audio_bytes, "audio/wav")
            if transcribed_speech and not transcribed_speech.startswith("Could not"):
                st.session_state.pending_prompt = transcribed_speech
                st.session_state.mic_seed += 1
                st.rerun()


# --- ACTIVE MODE & ATTACHMENT PILL BADGES ---
badge_cols = st.columns([0.8, 0.2])
has_badge = False

if st.session_state.active_mode == "image":
    has_badge = True
    badge_cols[0].markdown('<div class="mode-badge">🎨 Creative Image Mode Active</div>', unsafe_allow_html=True)
    if badge_cols[1].button("✕ Cancel Mode", key="cancel_img_mode"):
        st.session_state.active_mode = None
        st.rerun()

elif st.session_state.active_mode == "empathy":
    has_badge = True
    badge_cols[0].markdown('<div class="mode-badge">🧠 Empathy & Wellness Mode Active</div>', unsafe_allow_html=True)
    if badge_cols[1].button("✕ Cancel Mode", key="cancel_empathy_mode"):
        st.session_state.active_mode = None
        st.rerun()

if st.session_state.attached_file:
    has_badge = True
    f_name = st.session_state.attached_file.get("name", "file")
    badge_cols[0].markdown(f'<div class="attachment-badge">📎 Attached: {f_name}</div>', unsafe_allow_html=True)
    if badge_cols[1].button("✕ Remove Attachment", key="remove_attachment_btn"):
        st.session_state.attached_file = None
        st.rerun()


# --- DYNAMIC CHATBAR PLACEHOLDER ---
if st.session_state.active_mode == "image":
    chat_placeholder = "Describe the artwork you want to create (e.g. 'A futuristic electric supercar in Tokyo')..."
elif st.session_state.active_mode == "empathy":
    chat_placeholder = "Share what is on your mind, I am here to listen and help you reset..."
elif st.session_state.attached_file:
    f_name = st.session_state.attached_file.get("name", "file")
    chat_placeholder = f"Ask anything about {f_name} (press Enter)..."
else:
    chat_placeholder = "Message Lakshya AI or click the 🎙️ mic above to speak..."


# --- UNIFIED SINGLE CHATBAR ---
user_input = st.chat_input(placeholder=chat_placeholder)

# Handle pending prompt from suggestion chips or direct voice recording
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    user_input = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if user_input:
    # 1. Image Mode Handling
    is_image_mode = (st.session_state.active_mode == "image")
    final_prompt = user_input
    if is_image_mode and not user_input.lower().startswith("generate an image"):
        final_prompt = f"Generate an image of {user_input}"
        st.session_state.active_mode = None

    # 2. Extract Attached Media Payloads
    img_bytes = None
    img_mime = "image/jpeg"
    aud_bytes = None
    aud_mime = "audio/wav"

    if st.session_state.attached_file:
        att = st.session_state.attached_file
        ext = att.get("ext", "")
        if ext in ["png", "jpg", "jpeg", "webp"]:
            img_bytes = att.get("bytes")
            img_mime = att.get("mime", "image/jpeg")
        elif ext in ["wav", "mp3", "m4a", "ogg"]:
            aud_bytes = att.get("bytes")
            aud_mime = att.get("mime", "audio/wav")

    determined_type = "image" if img_bytes else ("audio" if aud_bytes else ("image_generation" if is_image_mode else "text"))

    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "input_type": determined_type,
        "sources": []
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 3. Request AI Response
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Lakshya is processing..."):
            start_time = time.time()
            resp = api_send_chat(
                prompt=final_prompt,
                conv_id=st.session_state.current_conversation_id,
                enable_rag=enable_rag,
                image_bytes=img_bytes,
                image_mime=img_mime,
                audio_bytes=aud_bytes,
                audio_mime=aud_mime,
            )
            elapsed = time.time() - start_time

            if resp:
                assistant_text = resp.get("response", "")
                gen_img_url = resp.get("generated_image_url")
                citations = resp.get("citations", [])
                asst_msg_id = resp.get("assistant_message_id", len(st.session_state.messages))

                st.markdown(assistant_text)
                st.caption(f"⚡ Replied in `{elapsed:.2f}s`")

                if gen_img_url:
                    img_file_path = None
                    if gen_img_url.startswith("/static/images/"):
                        img_name = gen_img_url.replace("/static/images/", "")
                        potential_path = BASE_DIR / "data" / "generated" / "images" / img_name
                        if potential_path.exists():
                            img_file_path = potential_path

                    if img_file_path and img_file_path.exists():
                        st.image(str(img_file_path), caption="Lakshya Generated Artwork", use_container_width=True)
                        with open(img_file_path, "rb") as f:
                            data_bytes = f.read()
                        st.download_button(
                            label="⬇️ Download High-Res Artwork",
                            data=data_bytes,
                            file_name=f"lakshya_{asst_msg_id}.jpg",
                            mime="image/jpeg",
                            key=f"dl_btn_{asst_msg_id}"
                        )
                    elif gen_img_url.startswith("http"):
                        st.image(gen_img_url, caption="Lakshya Generated Artwork", use_container_width=True)

                if citations:
                    with st.expander(f"📚 Verified Citations ({len(citations)})", expanded=False):
                        for cite_idx, cite in enumerate(citations, 1):
                            title = cite.get("source_title", "Document")
                            score = cite.get("score")
                            score_str = f" • Similarity: `{score:.2f}`" if score is not None else ""
                            st.markdown(f"**[{cite_idx}] {title}**{score_str}")
                            st.info(f"\"{cite.get('snippet', '')}\"")

                if auto_speak:
                    with st.spinner("Synthesizing neural voice..."):
                        audio_data = api_synthesize_speech(assistant_text)
                        if audio_data:
                            st.session_state.audio_cache[asst_msg_id] = audio_data
                            st.audio(audio_data, format="audio/mp3")

                st.session_state.current_conversation_id = resp.get("conversation_id")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "input_type": resp.get("input_type", "text"),
                    "sources": citations,
                    "message_id": asst_msg_id,
                    "generated_image_url": gen_img_url,
                    "media_url": gen_img_url
                })

                st.session_state.attached_file = None
                st.rerun()
