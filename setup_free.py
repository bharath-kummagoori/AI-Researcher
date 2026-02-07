#!/usr/bin/env python3
"""
AI-Researcher Free Setup Script
Cross-platform setup (Windows, Mac, Linux) with free Ollama LLM backend.
"""
import os
import sys
import shutil
import subprocess
import platform


def check_python():
    """Check Python version."""
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version < (3, 10):
        print("  [ERROR] Python 3.10+ is required.")
        sys.exit(1)
    return True


def check_ollama():
    """Check if Ollama is installed."""
    ollama_path = shutil.which("ollama")
    if ollama_path:
        print(f"  Ollama found at: {ollama_path}")
        return True
    else:
        print("  [NOT FOUND] Ollama is not installed.")
        print("  Install from: https://ollama.com/download")
        if platform.system() == "Windows":
            print("  Download: https://ollama.com/download/OllamaSetup.exe")
        elif platform.system() == "Darwin":
            print("  Run: brew install ollama")
        else:
            print("  Run: curl -fsSL https://ollama.com/install.sh | sh")
        return False


def pull_ollama_model(model_name="llama3.1:8b"):
    """Pull an Ollama model."""
    try:
        print(f"  Pulling {model_name}...")
        subprocess.run(["ollama", "pull", model_name], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  [WARNING] Could not pull {model_name}. Make sure Ollama is running.")
        return False


def install_dependencies():
    """Install Python dependencies."""
    print("  Installing core dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        return True
    except subprocess.CalledProcessError:
        print("  [WARNING] Full install failed. Trying core packages...")
        core_packages = [
            "numpy", "openai", "litellm==1.55.0", "beautifulsoup4",
            "chromadb", "click", "gradio", "httpx", "loguru",
            "matplotlib", "pandas", "pydantic", "PyYAML", "rich",
            "tenacity", "tiktoken", "sentence_transformers", "arxiv",
            "requests", "tqdm", "python-dotenv"
        ]
        subprocess.run([sys.executable, "-m", "pip", "install"] + core_packages, check=True)
        return True


def setup_env_file():
    """Create .env from template if it doesn't exist."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.template"):
            shutil.copy2(".env.template", ".env")
            print("  Created .env from template (free Ollama defaults)")
        else:
            print("  [WARNING] .env.template not found")
    else:
        print("  .env already exists, skipping...")


def main():
    print("=" * 50)
    print("  AI-Researcher - Free Setup")
    print("=" * 50)
    print()

    print("[1/5] Checking Python...")
    check_python()
    print()

    print("[2/5] Installing dependencies...")
    install_dependencies()
    print()

    print("[3/5] Setting up environment file...")
    setup_env_file()
    print()

    print("[4/5] Checking Ollama (free LLM backend)...")
    has_ollama = check_ollama()
    print()

    if has_ollama:
        print("[5/5] Pulling Ollama model (llama3.1:8b, ~4.7GB)...")
        pull_ollama_model()
    else:
        print("[5/5] Skipping model pull (install Ollama first)")
    print()

    print("=" * 50)
    print("  Setup Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    if not has_ollama:
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Pull a model: ollama pull llama3.1:8b")
        print("  3. Start Ollama: ollama serve")
    else:
        print("  1. Start Ollama: ollama serve")
    print(f"  {'4' if not has_ollama else '2'}. Run: python web_ai_researcher.py")
    print(f"  {'5' if not has_ollama else '3'}. Open: http://127.0.0.1:7039")
    print()
    print("Total cost: $0 (everything runs locally!)")
    print()


if __name__ == "__main__":
    main()
