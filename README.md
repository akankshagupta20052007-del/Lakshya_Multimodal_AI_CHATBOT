# ⚡ Lakshya Multimodal AI Studio

> **Executive-Grade Multimodal AI Studio** powered by Google Gemini, FastAPI, Streamlit, and SQLAlchemy.

---

## 🌟 Highlights & Architecture

1. **Single Centralized API Key**
   - A single `GEMINI_API_KEY` in `.env` powers:
     - 💬 Text Chat & Empathy Engine (`gemini-3.5-flash-lite` with dynamic fallbacks)
     - 👁️ Multimodal Vision (Image understanding & OCR)
     - 🎙️ Speech-to-Text (Voice audio transcription)
     - 📚 Grounded RAG Context Embeddings & Citations
2. **Gemini-Enhanced Creative Image Generation**
   - Generates authentic artwork strictly following your prompt.
   - **Prompt Intelligence**: Automatically fixes typos (e.g., `"imag eo fmodi ji"` -> `"Narendra Modi"`), interprets shorthand/Hindi, and creates vivid photorealistic visual prompts.
   - **No Stock Placeholders & Banner Suppression**: Never returns random photos or yellow error banners.
   - **Smart Cooldown Countdown**: Informs you of exact cooldown seconds remaining on free tiers.
   - Automatically saves artwork to `./data/generated/images/` with instant one-click download buttons.
3. **Direct Chatbar Microphone (STT) & Neural Voice (TTS)**
   - 🎙️ **Direct Chatbar Mic**: Click the microphone right beside the chat input to speak. Transcribes voice live and automatically sends into the conversation.
   - 🔊 **Zero-Key Neural Voice (TTS)**: High-fidelity natural voice powered by `edge-tts` (Aria Neural) with `gTTS` fallback.
4. **Grounded RAG Knowledge Base**
   - Upload PDF, TXT, or MD documents.
   - Automatically chunks (600 characters with 100 character overlap) and indexes documents.
   - Returns verifiable source citations and similarity scores in expandable citation cards.
5. **Priority Safety Intervention**
   - Bypasses LLM calls immediately when crisis/self-harm prompts are detected to provide **988 Suicide & Crisis Lifeline** resources.
6. **Executive Obsidian UI**
   - Obsidian Slate dark mode with subtle electric indigo/cyan neon accents.
   - Glowing holographic AI Core with pulse & orbital ring animations.
   - Unified sticky chatbar dock with one-click Studio Tools and direct microphone recording.

---

## 🚀 Quick Start (One-Click)

### Option A: One-Click Windows Launcher (`start.bat`)
Simply double-click:
```bat
start.bat
```
This automatically launches:
- **FastAPI Backend Server**: `http://127.0.0.1:8000`
- **Streamlit Studio**: `http://localhost:8501`
- Opens `http://localhost:8501` in your default browser automatically!

---

### Option B: Windows PowerShell Commands

1. **Navigate to the project folder:**
   ```powershell
   cd D:\chatbot\multimodal-chatbot
   ```

2. **Start the FastAPI Backend:**
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

3. **In a second PowerShell window, start the Streamlit UI:**
   ```powershell
   python -m streamlit run streamlit_app.py --server.port 8501
   ```

4. **Open your browser:**
   ```
   http://localhost:8501
   ```

---

## 🐙 How to Push to GitHub from VS Code

Follow these simple steps to push this project to your GitHub account:

### Method 1: Using the VS Code Interface (Easiest)

1. **Open VS Code:**
   - In VS Code, open the folder: `D:\chatbot\multimodal-chatbot` (`File` -> `Open Folder...`).
2. **Open Source Control Panel:**
   - Click the **Source Control** icon on the left activity bar (or press `Ctrl + Shift + G`).
3. **Stage All Changes:**
   - Hover over **Changes** and click the **`+` (Stage All Changes)** icon.
   - *(Note: Your `.env` and database files are automatically protected by `.gitignore` and will never be uploaded).*
4. **Write Commit Message & Commit:**
   - In the text box at the top, type: `Initial commit: Lakshya Multimodal AI Studio`
   - Click the blue **Commit** button (or press `Ctrl + Enter`).
5. **Publish to GitHub:**
   - Click the **Publish Branch** button that appears.
   - Choose **Publish to GitHub public repository** (or private if you prefer).
   - VS Code will prompt you to sign in to your GitHub account and will automatically create the repository and push all files!

---

### Method 2: Using the VS Code Terminal (Git CLI)

1. Open the integrated terminal in VS Code (`Ctrl + ~`) and ensure you are in `D:\chatbot\multimodal-chatbot`:
   ```powershell
   cd D:\chatbot\multimodal-chatbot
   ```
2. Create your repository on [GitHub](https://github.com/new) (e.g. named `lakshya-multimodal-studio`).
3. Run the following commands:
   ```powershell
   # 1. Stage all project files
   git add .

   # 2. Commit the changes
   git commit -m "feat: complete Lakshya Multimodal AI Studio"

   # 3. Set your main branch
   git branch -M main

   # 4. Link your GitHub remote repository (replace with your repo URL)
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git

   # 5. Push to GitHub
   git push -u origin main
   ```

---

## 📂 Directory Layout

```
multimodal-chatbot/
├── app/
│   ├── main.py              # FastAPI app & static media mounting
│   ├── config.py            # Configuration & single GEMINI_API_KEY loader
│   ├── database.py          # SQLAlchemy engine with SQLite auto-fallback
│   ├── models/              # Conversation, Message, Document, MessageSource
│   ├── schemas/             # Pydantic v2 schemas
│   ├── routers/             # chat.py, documents.py, conversations.py, media.py
│   ├── services/
│   │   ├── llm.py           # Gemini 3.5 Flash Lite + fallback chain + empathy
│   │   ├── multimodal.py    # Image vision analysis
│   │   ├── image_gen.py     # Prompt-adherent image synthesis & rate limit defense
│   │   ├── speech.py        # STT audio transcription & zero-key TTS voice synthesis
│   │   ├── rag.py           # Chunking, indexing, and grounded retrieval
│   │   └── safety.py        # Crisis detection (988), injection defense, validation
├── frontend/
│   └── streamlit_app.py     # Executive Dark theme, floating AI core, unified chatbar
├── streamlit_app.py         # Root entry point for Streamlit
├── knowledge_base/          # Source documents for RAG context
├── data/                    # Generated media, database, and vector index
├── tests/                   # Automated pytest suite (13 tests)
├── requirements.txt         # Pinned dependencies
├── start.bat                # One-click Windows startup script
├── .env.example
├── .gitignore
└── README.md
```
