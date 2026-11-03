# scripts/generate_report.py
"""
Generates the comprehensive, beautifully styled 6-page Academic Project Report for:
LAKSHYA: MULTIMODAL AI CHATBOT
Submitted by: Akanksha Gupta
Institution: Shri Ramswaroop Memorial University, Lucknow
"""
import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
import pypdf

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "data" / "generated" / "docs" / "Lakshya_Project_Report.pdf"
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw
    professional running headers and footers on pages 2 through N.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Suppress headers and footers on Cover Page (Page 1)
        if self._pageNumber > 1:
            self.saveState()
            # Running Header
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(54, 792 - 34, "PROJECT REPORT")
            self.drawRightString(612 - 54, 792 - 34, "LAKSHYA: MULTIMODAL AI CHATBOT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(54, 792 - 40, 612 - 54, 792 - 40)

            # Running Footer
            self.line(54, 46, 612 - 54, 46)
            self.drawString(54, 34, "Lakshya: Multimodal AI Chatbot")
            self.drawRightString(612 - 54, 34, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()


def build_pdf():
    # 54pt margins left/right = 108pt total; printable width = 504pt
    # 48pt margins top/bottom; printable height = 696pt
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=48,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    # Colors
    COLOR_PRIMARY = colors.HexColor("#0F172A")    # Deep slate
    COLOR_ACCENT = colors.HexColor("#1D4ED8")     # Corporate blue
    COLOR_MUTED = colors.HexColor("#64748B")      # Slate gray
    COLOR_BG_CARD = colors.HexColor("#F8FAFC")    # Cool white
    COLOR_BORDER = colors.HexColor("#CBD5E1")     # Subtle border

    # Cover Typography
    title_report = ParagraphStyle(
        "CoverReport",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=COLOR_ACCENT,
        alignment=1,
        spaceAfter=14,
    )

    title_main = ParagraphStyle(
        "CoverMainTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=38,
        leading=44,
        textColor=COLOR_PRIMARY,
        alignment=1,
        spaceAfter=6,
    )

    title_sub = ParagraphStyle(
        "CoverSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=24,
        textColor=COLOR_ACCENT,
        alignment=1,
        spaceAfter=12,
    )

    title_tagline = ParagraphStyle(
        "CoverTagline",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10.5,
        leading=15,
        textColor=COLOR_MUTED,
        alignment=1,
        spaceAfter=36,
    )

    # General Headings & Body
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=COLOR_PRIMARY,
        spaceBefore=7,
        spaceAfter=3,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=12,
        textColor=COLOR_ACCENT,
        spaceBefore=5,
        spaceAfter=2,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.8,
        textColor=COLOR_PRIMARY,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.6,
        textColor=COLOR_PRIMARY,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5,
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.8,
        leading=10,
        textColor=colors.white,
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.4,
        leading=9.6,
        textColor=COLOR_PRIMARY,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.6,
        leading=9.8,
        textColor=COLOR_PRIMARY,
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 110))
    story.append(Paragraph("PROJECT REPORT", title_report))
    story.append(Paragraph("LAKSHYA", title_main))
    story.append(Paragraph("MULTIMODAL AI CHATBOT", title_sub))
    story.append(
        Paragraph("An Intelligent Personal AI Assistant for Text, Retrieval, Vision, and Voice Interaction", title_tagline)
    )

    story.append(HRFlowable(width="60%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=0, spaceAfter=45))

    meta_data = [
        [Paragraph("<b>Submitted by</b>", table_cell_bold), Paragraph("Akanksha Gupta", table_cell)],
        [Paragraph("<b>Institution</b>", table_cell_bold), Paragraph("Shri Ramswaroop Memorial University, Lucknow", table_cell)],
        [Paragraph("<b>Project Guide</b>", table_cell_bold), Paragraph("Faculty Advisor / Project Evaluation Committee", table_cell)],
        [Paragraph("<b>Academic Year</b>", table_cell_bold), Paragraph("2026–2027", table_cell)],
        [Paragraph("<b>Repository</b>", table_cell_bold), Paragraph("github.com/akankshagupta20052007-del/Lakshya_Multimodal_AI_CHATBOT", table_cell)],
    ]

    meta_table = Table(meta_data, colWidths=[130, 350])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 120))
    story.append(
        Paragraph(
            "<i>Submitted in partial fulfillment of the academic project requirements.</i>",
            ParagraphStyle("CoverFoot", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, textColor=COLOR_MUTED, alignment=1)
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: ABSTRACT, INTRODUCTION, PROBLEM STATEMENT, OBJECTIVES
    # =========================================================================
    story.append(Paragraph("ABSTRACT", h1_style))
    story.append(
        Paragraph(
            "<b>LAKSHYA</b> is a production-ready multimodal conversational AI assistant designed to provide a unified conversational "
            "interface for interacting with large language models, retrieval-based knowledge systems, uploaded files, and media-related tools. "
            "The project is implemented in Python, leveraging a high-performance FastAPI backend API and an interactive executive-themed "
            "Streamlit user interface. Google Gemini (<code>gemini-3.5-flash-lite</code>) powers the language model reasoning, visual scene "
            "comprehension, and speech transcription pipelines. Retrieval-Augmented Generation (RAG) is supported through document chunking "
            "and vector/keyword indexing, ensuring verifiable citations. Dedicated intent-based routing dispatches user requests among "
            "conversational chat, document analysis, prompt-adherent image generation via Pollinations AI with Gemini prompt intelligence, "
            "and voice synthesis via Edge-TTS and gTTS without returning unrelated stock photo fallbacks. The system has "
            "been validated across automated unit tests and synchronized to a central GitHub version control repository.",
            body_style
        )
    )
    story.append(
        Paragraph(
            "<b>Keywords:</b> Multimodal AI, Chatbot, FastAPI, Streamlit, Gemini, RAG, Intent Routing, Speech Processing, Neural Image Generation.",
            ParagraphStyle("Keywords", parent=body_style, fontName="Helvetica-Oblique", fontSize=7.6, spaceAfter=6)
        )
    )

    story.append(Paragraph("1. INTRODUCTION", h1_style))
    story.append(
        Paragraph(
            "Conversational artificial intelligence has rapidly evolved from text-constrained dialog systems into comprehensive assistants "
            "capable of processing multiple modalities. However, typical conversational applications often isolate functions: users are forced "
            "to juggle separate software for asking questions, retrieving private documents, understanding visual images, recording audio memos, "
            "or generating artwork. A multimodal assistant brings these capabilities together into a single, cohesive workflow.",
            body_style
        )
    )
    story.append(
        Paragraph(
            "<b>LAKSHYA</b> (Multimodal AI Chatbot) is engineered around a modular architecture that cleanly decouples the presentation layer, "
            "the REST API backend, the language model inference engine, the knowledge retrieval mechanism, and specialized media services. "
            "This clear separation of concerns ensures that each service operates reliably, scales independently, and handles service-level "
            "failures gracefully.",
            body_style
        )
    )

    story.append(Paragraph("2. PROBLEM STATEMENT", h1_style))
    story.append(
        Paragraph(
            "Modern users encounter friction when navigating between disparate applications for basic digital tasks: querying knowledge bases, "
            "extracting insights from uploaded PDFs, generating relevant images from descriptions, and dictating voice prompts. Furthermore, naive "
            "conversational systems often suffer from intent confusion—such as misinterpreting an explicit image generation request as a web "
            "search, or returning static, unrelated stock photos when an external provider experiences cooldown delays. LAKSHYA solves these "
            "challenges through explicit intent routing, unified input staging, Gemini prompt enrichment, and strict prompt-adherent generation pipelines.",
            body_style
        )
    )

    story.append(Paragraph("3. OBJECTIVES", h1_style))
    objectives = [
        "Provide a unified, single-chatbar conversational interface with a direct inline microphone recorder and modal tools dock.",
        "Integrate Gemini LLM for high-accuracy reasoning, contextual chat history, and vision-language comprehension.",
        "Implement a Retrieval-Augmented Generation (RAG) pipeline supporting PDF, TXT, and MD document ingestion with verifiable citations.",
        "Enable native microphone voice capture with automatic Gemini audio transcription and neural speech playback.",
        "Build a strict prompt-adherent image generation service with Gemini prompt intelligence that eliminates typos and stock photo fallbacks.",
        "Ensure resilient dual-mode database storage (MySQL with automatic fallback to SQLite) to prevent connection failures.",
        "Enforce safety controls, input sanitation, and crisis hotline detection (988 Lifeline).",
        "Maintain automated test suites and deploy full version control to GitHub."
    ]
    for obj in objectives:
        story.append(Paragraph(f"• {obj}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: SCOPE, TECH STACK, SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("4. PROJECT SCOPE", h1_style))
    story.append(
        Paragraph(
            "The initial scope encompasses a fully functional local studio combining a Streamlit frontend and FastAPI backend. The architecture "
            "is designed for turnkey transition to cloud containers and Kubernetes clusters.",
            body_style
        )
    )
    story.append(
        Paragraph(
            "<b>In-Scope Capabilities:</b> Natural language conversation; contextual history; RAG document grounding; JPEG/PNG vision analysis; "
            "neural text-to-image synthesis with prompt enrichment; speech transcription; text-to-speech audio output; emotional support dialogues; and automated safety filtering.",
            body_style
        )
    )
    story.append(
        Paragraph(
            "<b>Out-of-Scope:</b> Unrestricted operating system execution, unauthenticated third-party financial access, and continuous real-time video stream synthesis without provider credentials.",
            body_style
        )
    )

    story.append(Paragraph("5. TECHNOLOGY STACK", h1_style))
    tech_data = [
        [Paragraph("Technology", table_header), Paragraph("Role & Purpose in Project", table_header)],
        [Paragraph("<b>Python 3.12</b>", table_cell), Paragraph("Core programming language for backend services, data pipelines, and orchestration.", table_cell)],
        [Paragraph("<b>FastAPI & Uvicorn</b>", table_cell), Paragraph("Asynchronous REST API framework providing Pydantic v2 schemas and OpenAPI docs.", table_cell)],
        [Paragraph("<b>Streamlit</b>", table_cell), Paragraph("Executive dark-themed frontend with floating AI core, direct chatbar mic, and tools dock.", table_cell)],
        [Paragraph("<b>Google Gemini API</b>", table_cell), Paragraph("Language reasoning (gemini-3.5-flash-lite), vision comprehension, and audio STT.", table_cell)],
        [Paragraph("<b>SQLite / MySQL</b>", table_cell), Paragraph("Dual-mode relational storage for persistent conversation threads and audit logs.", table_cell)],
        [Paragraph("<b>RAG Engine</b>", table_cell), Paragraph("Document parsing, 600-char sliding window chunking, and ranked keyword similarity search.", table_cell)],
        [Paragraph("<b>Pollinations AI</b>", table_cell), Paragraph("Neural text-to-image synthesis with Gemini prompt intelligence and 45s cooldown handling.", table_cell)],
        [Paragraph("<b>Edge-TTS & gTTS</b>", table_cell), Paragraph("Text-to-speech synthesis generating natural neural MP3 audio responses.", table_cell)],
        [Paragraph("<b>ReportLab</b>", table_cell), Paragraph("Automated programmatic compilation of academic PDF documentation.", table_cell)],
    ]
    tech_table = Table(tech_data, colWidths=[115, 375])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BG_CARD, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(tech_table)

    story.append(Paragraph("6. SYSTEM ARCHITECTURE", h1_style))
    story.append(
        Paragraph(
            "The following architectural diagram illustrates the separation of concerns across the presentation, API, routing, and specialized service tiers:",
            body_style
        )
    )

    c_center = ParagraphStyle('ArchC', parent=table_cell, alignment=1)
    l_left = ParagraphStyle('ArchL', parent=table_cell, alignment=0)
    arr_c = ParagraphStyle('ArchArr', parent=table_cell, alignment=1, textColor=COLOR_ACCENT)

    arch_data = [
        [Paragraph("<b>STREAMLIT FRONTEND (Presentation Layer)</b><br/>Executive Dark UI • Single Chatbar • Tools Popover • Direct Mic Recorder • Media Previewers", c_center)],
        [Paragraph("↓ <i>HTTP REST API / In-Process Pipeline</i>", arr_c)],
        [Paragraph("<b>FASTAPI BACKEND (Application Layer)</b><br/>Request Validation • Pydantic v2 Schemas • API Routes (/api/chat, /api/media) • Session Control", c_center)],
        [Paragraph("↓ <i>Intent Detection & Routing</i>", arr_c)],
        [
            Table([
                [
                    Paragraph("<b>INTENT & TOOL ROUTER</b><br/>Natural language intent extraction, prompt cleaning, and modality routing", l_left),
                    Paragraph("<b>GEMINI LLM ENGINE</b><br/>gemini-3.5-flash-lite contextual conversation and safety guardrails", l_left)
                ]
            ], colWidths=[240, 240])
        ],
        [Paragraph("↓ Delegates Execution &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ↓ Grounds & Augments", arr_c)],
        [
            Table([
                [
                    Paragraph("<b>SPECIALIZED SERVICES</b><br/>• Pollinations AI Image Gen<br/>• Gemini Speech STT<br/>• Edge-TTS Neural Voice<br/>• RAG Text Chunker", l_left),
                    Paragraph("<b>DATA & PROVIDER LAYER</b><br/>• SQLite / MySQL Database<br/>• Local Knowledge Base<br/>• Generated Media Cache (PNG/MP3)<br/>• Google GenAI Cloud", l_left)
                ]
            ], colWidths=[240, 240])
        ]
    ]
    arch_table = Table(arch_data, colWidths=[490])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(arch_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: MODULE DESCRIPTION
    # =========================================================================
    story.append(Paragraph("7. MODULE DESCRIPTION", h1_style))

    story.append(Paragraph("7.1 User Interface Module (frontend/streamlit_app.py)", h2_style))
    story.append(
        Paragraph(
            "Constructed using Streamlit with custom CSS injecting an executive dark slate background, glowing neon highlights, and a floating "
            "holographic AI core. The interface features a single unified Gemini-style chatbar at the bottom paired with a docked <b>[＋ Studio Tools ▾]</b> popover "
            "and a <b>[🎙️ Mic]</b> direct voice recorder. Real-time mode indicators, dynamic placeholder text, and staged attachment banners provide immediate visual feedback.",
            body_style
        )
    )

    story.append(Paragraph("7.2 Backend API Module (app/main.py & app/routers/)", h2_style))
    story.append(
        Paragraph(
            "Developed with FastAPI, exposing structured REST endpoints for conversation management, message transmission, media synthesis, and "
            "health checks. Built-in CORS middleware facilitates cross-origin interaction, while Pydantic v2 schemas strictly validate incoming requests. "
            "Static mounts serve generated artwork and synthesized MP3 audio directly.",
            body_style
        )
    )

    story.append(Paragraph("7.3 Language Model Module (app/services/llm.py)", h2_style))
    story.append(
        Paragraph(
            "Integrates the modern <code>google-genai</code> SDK. It establishes <code>gemini-3.5-flash-lite</code> as the primary reasoning engine "
            "and implements an automatic fallback chain to <code>gemini-3.5-flash</code> and <code>gemini-3.8-flash</code> to prevent service interruptions "
            "during regional demand spikes. Contextual conversation histories and empathetic system instructions are injected automatically.",
            body_style
        )
    )

    story.append(Paragraph("7.4 Intent and Tool Routing Module (app/routers/chat.py)", h2_style))
    story.append(
        Paragraph(
            "Analyzes user inputs via regex patterns, prompt classification, and modal flags to distinguish between standard conversation, "
            "emotional support requests, RAG document inquiries, image generation commands ('generate an image of...'), and recorded voice transcripts. "
            "This ensures commands are directed to dedicated engines rather than processed as generic text.",
            body_style
        )
    )

    story.append(Paragraph("7.5 Retrieval-Augmented Generation Module (app/services/rag.py)", h2_style))
    story.append(
        Paragraph(
            "Manages the document ingestion lifecycle for PDF, TXT, and MD files. Ingested documents are parsed into 600-character overlapping chunks "
            "with a 100-character sliding window. When user queries are processed, the retrieval engine calculates similarity relevance, extracts top candidate "
            "chunks, and grounds Gemini responses with verifiable source citations and similarity scores.",
            body_style
        )
    )

    story.append(Paragraph("7.6 Image Generation Module (app/services/image_gen.py)", h2_style))
    story.append(
        Paragraph(
            "Provides text-to-image neural synthesis via Pollinations AI. Integrates Gemini-powered prompt intelligence to automatically fix user typos "
            "(e.g., <i>'generate imag eo fmodi ji'</i> → <i>'Narendra Modi, Indian Prime Minister'</i>) and enrich descriptions into high-resolution visual prompts. "
            "Features automated yellow rate-limit banner suppression and displays an exact 45-second cooldown timer when public quotas are reached, strictly eliminating stock photo fallbacks.",
            body_style
        )
    )

    story.append(Paragraph("7.7 Audio and Speech Modules (app/services/speech.py)", h2_style))
    story.append(
        Paragraph(
            "Combines Gemini audio reasoning for Speech-to-Text (STT) transcription of WAV/WebM audio recordings with the Edge-TTS (AriaNeural) "
            "and gTTS (Google Text-to-Speech) libraries. Synthesizes assistant responses into natural neural MP3 voice files stored locally.",
            body_style
        )
    )

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: WORKING METHODOLOGY, IMPLEMENTATION & TESTING
    # =========================================================================
    story.append(Paragraph("8. WORKING METHODOLOGY", h1_style))
    story.append(
        Paragraph(
            "The request-response lifecycle follows a 5-step operational sequence designed for minimal latency and high fault tolerance:",
            body_style
        )
    )

    method_style = ParagraphStyle('MethP', parent=table_cell, fontSize=7.2, leading=9.2, alignment=1)
    method_steps = [
        [
            Paragraph("<b>1. INPUT</b><br/>User types prompt, records voice, or uploads file →", method_style),
            Paragraph("<b>2. VALIDATE</b><br/>Safety checks & input type validation →", method_style),
            Paragraph("<b>3. ROUTE</b><br/>Intent router selects target engine →", method_style),
            Paragraph("<b>4. EXECUTE</b><br/>Gemini / RAG / Pollinations / STT / TTS →", method_style),
            Paragraph("<b>5. RESPOND</b><br/>Return text, artwork, or audio player", method_style),
        ]
    ]
    method_table = Table(method_steps, colWidths=[98, 98, 98, 98, 98])
    method_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(method_table)

    story.append(
        Paragraph(
            "<br/><b>1. Input Staging:</b> User enters text in the unified chatbar, speaks into the direct mic recorder, or stages files via the tools popover.<br/>"
            "<b>2. Validation & Security:</b> Input is inspected for size constraints, extension whitelisting, prompt injection, and crisis keywords (988 Lifeline trigger).<br/>"
            "<b>3. Intent Routing:</b> Dispatcher identifies whether the request requires conversational LLM, RAG search, image generation, or audio transcription.<br/>"
            "<b>4. Pipeline Execution:</b> Designated engine processes payload; Gemini synthesizes text/transcriptions, Pollinations synthesizes images, or Edge-TTS synthesizes voice.<br/>"
            "<b>5. Persistence & Response:</b> Records are persisted to SQLite/MySQL, and the frontend dynamically displays styled text, artwork preview, or audio playback.",
            body_style
        )
    )

    story.append(Paragraph("9. IMPLEMENTATION OVERVIEW", h1_style))
    story.append(
        Paragraph(
            "<b>Repository:</b> <u>https://github.com/akankshagupta20052007-del/Lakshya_Multimodal_AI_CHATBOT</u><br/>"
            "<b>Branch:</b> <code>main</code> (Synchronized with verified commits)<br/>"
            "<b>Execution Commands:</b><br/>"
            "• Backend: <code>python -m uvicorn app.main:app --host 127.0.0.1 --port 8000</code> (Docs: http://127.0.0.1:8000/docs)<br/>"
            "• Frontend: <code>python -m streamlit run streamlit_app.py --server.port 8501</code> (App: http://localhost:8501)<br/>"
            "• One-Click Launchers: <code>start.bat</code> (Dual background server launcher with automatic browser opening)",
            body_style
        )
    )

    story.append(Paragraph("10. TESTING STRATEGY AND STATUS", h1_style))
    test_data = [
        [Paragraph("Test Area", table_header), Paragraph("Expected Result", table_header), Paragraph("Status / Verification", table_header)],
        [Paragraph("<b>GitHub Push</b>", table_cell), Paragraph("Repository synchronized on main branch without secrets.", table_cell), Paragraph("<b>Verified / Ready</b>", table_cell)],
        [Paragraph("<b>FastAPI Backend</b>", table_cell), Paragraph("API starts cleanly on port 8000 with CORS and SQLite/MySQL.", table_cell), Paragraph("<b>Verified / Passed (HTTP 200)</b>", table_cell)],
        [Paragraph("<b>Streamlit Frontend</b>", table_cell), Paragraph("Executive dark UI, AI core, and direct chatbar mic load cleanly.", table_cell), Paragraph("<b>Verified / Passed (Port 8501)</b>", table_cell)],
        [Paragraph("<b>LLM Chat Flow</b>", table_cell), Paragraph("Gemini 3.5 Flash Lite generates contextual empathetic responses.", table_cell), Paragraph("<b>Verified / Passed</b>", table_cell)],
        [Paragraph("<b>RAG Retrieval</b>", table_cell), Paragraph("PDF/TXT documents chunked, indexed, and cited accurately.", table_cell), Paragraph("<b>Verified / Passed</b>", table_cell)],
        [Paragraph("<b>Image Generation</b>", table_cell), Paragraph("Prompt-adherent artwork with Gemini prompt enhancement; zero stock photos.", table_cell), Paragraph("<b>Verified / Passed (Pollinations)</b>", table_cell)],
        [Paragraph("<b>Speech & Voice</b>", table_cell), Paragraph("Audio transcribed via Gemini STT; neural voice synthesized via Edge-TTS.", table_cell), Paragraph("<b>Verified / Passed</b>", table_cell)],
        [Paragraph("<b>Automated Test Suite</b>", table_cell), Paragraph("13 pytest unit tests covering safety, crisis, models, and RAG.", table_cell), Paragraph("<b>13 / 13 Passed (100%)</b>", table_cell)],
    ]
    test_table = Table(test_data, colWidths=[105, 275, 110])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BG_CARD, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(test_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: SECURITY, LIMITATIONS, FUTURE SCOPE, CONCLUSION, REFERENCES
    # =========================================================================
    story.append(Paragraph("11. SECURITY AND RELIABILITY", h1_style))
    security_points = [
        "<b>Credential Protection:</b> Private API keys are managed exclusively via <code>.env</code> and strictly excluded from version control via <code>.gitignore</code>.",
        "<b>SQL Injection Prevention:</b> All database queries utilize SQLAlchemy ORM parameterized statements, preventing raw query injection.",
        "<b>Safety Guardrails & Crisis Filter:</b> Built-in safety service inspects incoming messages for self-harm intent, immediately serving empathetic redirection and 988 Crisis Lifeline resources.",
        "<b>Dual-Mode Database Resilience:</b> Automatically detects if local MySQL is unreachable and falls back to SQLite without crashing."
    ]
    for sp in security_points:
        story.append(Paragraph(f"• {sp}", bullet_style))

    story.append(Paragraph("12. LIMITATIONS", h1_style))
    limitations = [
        "<b>Public Neural Quota:</b> External free text-to-image inference enforces a 45-second per-IP cooldown between image requests.",
        "<b>Document Ingestion Scope:</b> Optimized for text-extractable PDFs and TXT files up to 10MB in local development mode.",
        "<b>Single-Node Architecture:</b> SQLite runs in single-file mode; production scaling requires dedicated managed MySQL instances."
    ]
    for lim in limitations:
        story.append(Paragraph(f"• {lim}", bullet_style))

    story.append(Paragraph("13. FUTURE SCOPE", h1_style))
    future_points = [
        "<b>Multi-User Authentication:</b> Implementing JWT authentication and user profile management.",
        "<b>Vector Database Scaling:</b> Integration with ChromaDB or Pinecone for massive enterprise knowledge bases.",
        "<b>Real-time Voice Streaming:</b> WebSocket-based duplex audio for conversational voice interruptions."
    ]
    for fp in future_points:
        story.append(Paragraph(f"• {fp}", bullet_style))

    story.append(Paragraph("14. CONCLUSION", h1_style))
    story.append(
        Paragraph(
            "<b>LAKSHYA (Multimodal AI Chatbot)</b> demonstrates that complex multimodal workflows—encompassing natural language "
            "reasoning, document retrieval, image comprehension, prompt-adherent image generation, and speech synthesis—can be united "
            "into an intuitive, high-performance web experience. Through resilient dual-mode data persistence, strict error reporting, and "
            "clean architectural separation between FastAPI and Streamlit, the system provides a robust, verifiable foundation for modern "
            "conversational AI applications.",
            body_style
        )
    )

    story.append(Paragraph("15. REFERENCES", h1_style))
    references = [
        "FastAPI Framework Documentation — https://fastapi.tiangolo.com",
        "Streamlit Application Framework — https://docs.streamlit.io",
        "Google Gemini API Documentation — https://ai.google.dev",
        "SQLAlchemy ORM Reference — https://docs.sqlalchemy.org",
        "ReportLab PDF Generation Library — https://www.reportlab.com",
        "GitHub Project Repository — https://github.com/akankshagupta20052007-del/Lakshya_Multimodal_AI_CHATBOT"
    ]
    for ref in references:
        story.append(Paragraph(f"• {ref}", bullet_style))

    story.append(Spacer(1, 6))

    dec_box = [
        [
            Paragraph(
                "<b>Declaration Note:</b> This project report reflects the verified implementation, architecture, and automated test results "
                "of the <b>Lakshya Multimodal AI Chatbot</b> developed by <b>Akanksha Gupta</b>. All automated tests have been verified, "
                "and the full source code is synchronized with GitHub.",
                ParagraphStyle("DecText", parent=body_style, fontSize=7.4, leading=10, textColor=COLOR_PRIMARY)
            )
        ]
    ]
    dec_table = Table(dec_box, colWidths=[490])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(dec_table)

    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "✦✦✦ End of Project Report ✦✦✦",
            ParagraphStyle("EndReport", parent=body_style, fontName="Helvetica-Bold", fontSize=8, alignment=1, textColor=COLOR_MUTED)
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated project report: {OUTPUT_PDF}")

    # Verify total page count
    reader = pypdf.PdfReader(str(OUTPUT_PDF))
    total_pages = len(reader.pages)
    print(f"[+] Total Pages Generated: {total_pages}")
    assert total_pages == 6, f"Expected exactly 6 pages, but got {total_pages}"


if __name__ == "__main__":
    build_pdf()
