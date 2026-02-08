@echo off
setlocal enabledelayedexpansion
title AI-Researcher - One-Click Free Setup
color 0A

echo.
echo  ============================================================
echo       AI-Researcher - Complete One-Click Setup (FREE)
echo  ============================================================
echo       Your Machine: Windows, i7-10850H, 32GB RAM
echo       Cost: $0 - Everything runs locally
echo  ============================================================
echo.

REM ============================================================
REM  STEP 1: Check Prerequisites
REM ============================================================
echo [Step 1/7] Checking prerequisites...
echo.

REM Check Git
where git >nul 2>&1
if errorlevel 1 (
    echo  [X] Git is NOT installed.
    echo      Download from: https://git-scm.com/download/win
    echo      Install it and re-run this script.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('git --version') do echo  [OK] %%i
)

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo  [X] Python is NOT installed.
    echo      Download from: https://www.python.org/downloads/
    echo      IMPORTANT: Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo  [OK] %%i
)

REM Check Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo  [X] Ollama is NOT installed.
    echo      Download from: https://ollama.com/download
    echo      Install it and re-run this script.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('ollama --version 2^>^&1') do echo  [OK] Ollama - %%i
)

echo.
echo  All prerequisites found!
echo.

REM ============================================================
REM  STEP 2: Use current directory as project root
REM ============================================================
echo [Step 2/7] Setting up project directory...
echo.

REM Use the directory where this script is located
set "INSTALL_DIR=%~dp0"
cd /d "%INSTALL_DIR%"
echo  [OK] Project directory: %INSTALL_DIR%
echo.

REM ============================================================
REM  STEP 3: Create Python virtual environment
REM ============================================================
echo [Step 3/7] Setting up Python virtual environment...
echo.

if not exist "venv\Scripts\activate.bat" (
    python -m venv venv
    if errorlevel 1 (
        echo  [X] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created
) else (
    echo  [OK] Virtual environment already exists
)

call venv\Scripts\activate.bat
echo  [OK] Virtual environment activated
echo.

REM ============================================================
REM  STEP 4: Install Python dependencies
REM ============================================================
echo [Step 4/7] Installing Python dependencies (this may take a few minutes)...
echo.

pip install --upgrade pip >nul 2>&1

pip install -e . 2>nul
if errorlevel 1 (
    echo  [!] Full install had issues, installing core packages...
    pip install numpy openai "litellm>=1.55.0" beautifulsoup4 chromadb click gradio httpx loguru matplotlib pandas pydantic PyYAML rich tenacity tiktoken sentence_transformers arxiv requests tqdm python-dotenv pdfminer.six PyPDF2 html2text markdownify backoff
    if errorlevel 1 (
        echo  [X] Failed to install dependencies.
        pause
        exit /b 1
    )
)
echo  [OK] Python dependencies installed
echo.

REM ============================================================
REM  STEP 5: Setup environment configuration
REM ============================================================
echo [Step 5/7] Configuring environment...
echo.

if not exist ".env" (
    copy .env.template .env >nul
    echo  [OK] Created .env with free Ollama defaults
) else (
    echo  [OK] .env already exists
)
echo.

REM ============================================================
REM  STEP 6: Pull Ollama model
REM ============================================================
echo [Step 6/7] Pulling free LLM model (llama3.1:8b, ~4.7GB one-time download)...
echo.

REM Start Ollama if not running
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if errorlevel 1 (
    echo  Starting Ollama service...
    start /B ollama serve >nul 2>&1
    timeout /t 3 /nobreak >nul
)

ollama pull llama3.1:8b
if errorlevel 1 (
    echo  [!] Model pull failed. Make sure Ollama is running.
    echo      Try: ollama serve (in a separate terminal)
    echo      Then: ollama pull llama3.1:8b
) else (
    echo  [OK] llama3.1:8b model ready
)
echo.

REM ============================================================
REM  STEP 7: Launch AI-Researcher
REM ============================================================
echo [Step 7/7] Launching AI-Researcher...
echo.
echo  ============================================================
echo       SETUP COMPLETE - Launching Web UI
echo  ============================================================
echo.
echo  The web interface will open at: http://127.0.0.1:7039
echo  Press Ctrl+C to stop the server.
echo.
echo  Total cost: $0
echo  ============================================================
echo.

start http://127.0.0.1:7039
python web_ai_researcher.py

pause
