@echo off
title Lakshya Multimodal AI Studio Launcher
echo =====================================================================
echo          Launching Lakshya Multimodal AI Studio (Production)
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Activate Python Environment if venv exists
if exist "venv\Scripts\activate.bat" (
    echo [*] Activating venv...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating .venv...
    call .venv\Scripts\activate.bat
) else (
    echo [*] Using system Python environment...
)

:: 2. Launch FastAPI Backend on Port 8000 in background console
echo [*] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Lakshya Backend API (Port 8000)" cmd /c "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info"

:: 3. Give backend 3 seconds to initialize
echo [*] Initializing database and services...
timeout /t 3 /nobreak >nul

:: 4. Launch Streamlit UI on Port 8501
echo [*] Starting Lakshya Studio UI on http://localhost:8501 ...
start "Lakshya Streamlit UI (Port 8501)" cmd /c "python -m streamlit run streamlit_app.py --server.port 8501 --server.headless false"

:: 5. Open browser automatically
echo [*] Opening Lakshya Studio in your default browser...
timeout /t 2 /nobreak >nul
start http://localhost:8501

echo.
echo =====================================================================
echo  Lakshya Multimodal AI Studio is now running!
echo  - Backend API:  http://127.0.0.1:8000
echo  - API Docs:     http://127.0.0.1:8000/docs
echo  - Studio UI:    http://localhost:8501
echo =====================================================================
echo.
