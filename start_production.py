# start_production.py
"""
Production Startup Script for Multimodal Chatbot
Launches FastAPI backend on port 8000 and Streamlit frontend on port 8501.
"""
import sys
import subprocess
import time
import requests
from pathlib import Path
from app.config import settings
from app.database import init_db

BASE_DIR = Path(__file__).resolve().parent


def verify_environment():
    print(f"[*] Initializing database tables for environment: {settings.APP_ENV}...")
    try:
        init_db()
        print("[+] Database tables initialized successfully.")
    except Exception as e:
        print(f"[-] Database initialization warning: {e}")


def start_backend():
    print(f"[*] Starting FastAPI Production Server on {settings.API_HOST}:{settings.API_PORT}...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        str(settings.API_HOST),
        "--port",
        str(settings.API_PORT),
        "--log-level",
        "info",
    ]
    return subprocess.Popen(backend_cmd, cwd=str(BASE_DIR))


def start_frontend():
    print(f"[*] Starting Streamlit Production UI on port {settings.STREAMLIT_PORT}...")
    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port",
        str(settings.STREAMLIT_PORT),
        "--server.headless",
        "true",
    ]
    return subprocess.Popen(frontend_cmd, cwd=str(BASE_DIR))


def main():
    verify_environment()
    backend_proc = start_backend()

    # Wait for backend to report healthy
    print("[*] Waiting for FastAPI backend to become ready...")
    ready = False
    for _ in range(15):
        time.sleep(1)
        try:
            res = requests.get(f"http://127.0.0.1:{settings.API_PORT}/api/health", timeout=2)
            if res.status_code == 200:
                print(f"[+] FastAPI backend is UP and HEALTHY! Status: {res.json().get('status')}")
                ready = True
                break
        except Exception:
            pass

    if not ready:
        print("[-] Warning: Backend took longer than expected to respond, proceeding with frontend startup.")

    frontend_proc = start_frontend()
    print("\n" + "=" * 60)
    print(" Multimodal Chatbot Production Services are RUNNING:")
    print(f" -> Backend API:      http://127.0.0.1:{settings.API_PORT}")
    print(f" -> Swagger Docs:     http://127.0.0.1:{settings.API_PORT}/docs")
    print(f" -> Streamlit Web UI: http://127.0.0.1:{settings.STREAMLIT_PORT}")
    print("=" * 60 + "\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n[*] Stopping production processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("[+] Processes stopped cleanly.")


if __name__ == "__main__":
    main()

