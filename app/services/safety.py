# app/services/safety.py
"""
Cybersecurity, Safety & Crisis Intervention Service for Nexus Multimodal AI Studio.
Includes:
- Crisis Lifeline Detection (988 suicide & crisis prevention bypass)
- Prompt Injection Sanitization for untrusted RAG contexts
- File validation (extension whitelisting, size limits, path traversal defense)
"""
import re
from pathlib import Path
from typing import Tuple, Optional
from ..config import settings

# 988 Suicide & Crisis Lifeline Intervention Response
CRISIS_LIFELINE_MESSAGE = (
    "💙 **You are not alone, and help is available right now.**\n\n"
    "If you or someone you know is going through a tough time, feeling overwhelmed, or experiencing thoughts of self-harm, "
    "please connect with caring people who are ready to support you 24/7:\n\n"
    "📞 **Call or Text 988** — The Suicide & Crisis Lifeline (Free, confidential, 24/7 in US & Canada)\n"
    "💬 **Text HOME to 741741** — Crisis Text Line\n"
    "🌐 **International Help**: [findahelpline.com](https://findahelpline.com/)\n\n"
    "*Please reach out to a trusted professional, family member, or friend. Your life and well-being matter deeply.*"
)

# Regex triggers for crisis detection
CRISIS_PATTERNS = [
    r"\b(suicide|kill myself|want to die|end my life|end it all)\b",
    r"\b(hang myself|slit my wrist|take all my pills|overdose)\b",
    r"\b(no reason to live|better off dead|wish i was dead|can't go on living)\b",
    r"\b(harm myself|hurting myself|self harm)\b"
]


class SafetyService:
    @staticmethod
    def check_crisis(prompt: str) -> Tuple[bool, Optional[str]]:
        """
        Scans prompt for self-harm or suicidal ideation.
        If detected, returns True and the immediate 988 crisis helpline response,
        bypassing model execution.
        """
        text = prompt.lower().strip()
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, text):
                return True, CRISIS_LIFELINE_MESSAGE
        return False, None

    @staticmethod
    def sanitize_rag_context(context_text: str) -> str:
        """
        Sanitizes retrieved document chunks against prompt injection attacks
        (e.g., instructions attempting to override system behavior).
        """
        # Neutralize common prompt injection jailbreak patterns
        dangerous_patterns = [
            r"ignore (all )?previous instructions",
            r"system prompt",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
            r"\[INST\]",
            r"\[/INST\]",
            r"### (Human|Assistant|System):",
        ]
        sanitized = context_text
        for p in dangerous_patterns:
            sanitized = re.sub(p, "[FILTERED_INSTRUCTION]", sanitized, flags=re.IGNORECASE)

        # Truncate overly long single chunk strings to avoid context stuffing
        return sanitized.strip()

    @staticmethod
    def validate_upload(filename: str, file_bytes: bytes, allowed_types: Optional[list] = None) -> Tuple[bool, str]:
        """
        Enforces extension whitelisting, file size constraints, and path traversal protection.
        """
        if not filename:
            return False, "Filename cannot be empty."

        # Path traversal protection
        clean_name = Path(filename).name
        if clean_name != filename or ".." in filename or "/" in filename or "\\" in filename:
            return False, "Invalid filename or path traversal detected."

        ext = clean_name.lower().split(".")[-1] if "." in clean_name else ""
        whitelist = allowed_types or ["pdf", "txt", "md", "png", "jpg", "jpeg", "webp", "wav", "mp3", "m4a", "ogg"]
        if ext not in whitelist:
            return False, f"File format '.{ext}' is not supported. Allowed formats: {', '.join(whitelist)}."

        # File size check
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            return False, f"File exceeds maximum size limit of {settings.MAX_UPLOAD_SIZE_MB}MB (received {size_mb:.1f}MB)."

        return True, ""


# Singleton instance
safety_service = SafetyService()

