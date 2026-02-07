@echo off
echo ============================================
echo   AI-Researcher - Windows Setup (FREE)
echo ============================================
echo.

REM Check Python version
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'" 2>nul
if errorlevel 1 (
    echo [WARNING] Python 3.11+ is recommended. You may encounter issues with older versions.
)

echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install -e . 2>nul
if errorlevel 1 (
    echo [WARNING] Some packages may have failed. Trying core dependencies only...
    pip install numpy openai litellm==1.55.0 beautifulsoup4 chromadb click gradio httpx loguru matplotlib pandas pydantic PyYAML rich tenacity tiktoken sentence_transformers arxiv requests tqdm python-dotenv
)

echo [4/6] Setting up environment file...
if not exist ".env" (
    copy .env.template .env
    echo Created .env from template (free Ollama configuration)
) else (
    echo .env already exists, skipping...
)

echo [5/6] Checking Ollama installation...
ollama --version 2>nul
if errorlevel 1 (
    echo.
    echo [IMPORTANT] Ollama is NOT installed.
    echo Please install Ollama from: https://ollama.com/download
    echo After installing, run: ollama pull llama3.1:8b
    echo.
) else (
    echo Ollama is installed. Pulling llama3.1:8b model...
    ollama pull llama3.1:8b
)

echo [6/6] Installing Playwright browsers (for web scraping)...
python -m playwright install chromium 2>nul
if errorlevel 1 (
    echo [WARNING] Playwright browser install failed. Web scraping features may not work.
)

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To run AI-Researcher:
echo   1. Make sure Ollama is running (ollama serve)
echo   2. Activate venv: venv\Scripts\activate
echo   3. Start the web UI: python web_ai_researcher.py
echo   4. Open browser: http://127.0.0.1:7039
echo.
echo Total cost: $0 (everything runs locally!)
echo ============================================
pause
