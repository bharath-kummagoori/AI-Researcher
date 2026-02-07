import os
from dotenv import load_dotenv
import global_state

load_dotenv()  # Load .env file

# utils:
def str_to_bool(value):
    """convert string to bool"""
    true_values = {'true', 'yes', '1', 'on', 't', 'y'}
    false_values = {'false', 'no', '0', 'off', 'f', 'n'}

    if isinstance(value, bool):
        return value

    if not value:
        return False

    value = str(value).lower().strip()
    if value in true_values:
        return True
    if value in false_values:
        return False
    return True  # default return True


DOCKER_WORKPLACE_NAME = os.getenv('DOCKER_WORKPLACE_NAME', 'workplace_meta')
GITHUB_AI_TOKEN = os.getenv('GITHUB_AI_TOKEN', None)
AI_USER = os.getenv('AI_USER', "ai-sin")
LOCAL_ROOT = os.getenv('LOCAL_ROOT', os.getcwd())

DEBUG = str_to_bool(os.getenv('DEBUG', True))

DEFAULT_LOG = str_to_bool(os.getenv('DEFAULT_LOG', True))
LOG_PATH = os.getenv('LOG_PATH', None)
LOG_PATH = global_state.LOG_PATH
EVAL_MODE = str_to_bool(os.getenv('EVAL_MODE', False))
BASE_IMAGES = os.getenv('BASE_IMAGES', "tjbtech1/paperapp:latest")

# ============ EXECUTION MODE ============
# "local" = Docker-free local execution (default, free)
# "docker" = Docker-based execution (original behavior)
EXECUTION_MODE = os.getenv('EXECUTION_MODE', 'local')

# ============ FREE LLM CONFIGURATION (Ollama) ============
# Default: Ollama local models (completely free, runs on your machine)
# To use Ollama: install from https://ollama.com then run: ollama pull llama3.1:8b
# For paid models, change to: gpt-4o-2024-08-06, openrouter/google/gemini-2.5-pro, etc.
COMPLETION_MODEL = os.getenv('COMPLETION_MODEL', "ollama/llama3.1:8b")
CHEEP_MODEL = os.getenv('CHEEP_MODEL', "ollama/llama3.1:8b")

# ============ EMBEDDING CONFIGURATION ============
# "local" = free sentence-transformers (default), "text-embedding-3-small" = paid OpenAI
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', "local")
# "Local" = free sentence-transformers, "OpenAI" = paid OpenAI embeddings API
EMBEDDING_PLATFORM = os.getenv('EMBEDDING_PLATFORM', 'Local')

# GPUS = os.getenv('GPUS', "all")
GPUS = os.getenv('GPUS', None)

PLATFORM = os.getenv('PLATFORM', 'linux/amd64')

FN_CALL = str_to_bool(os.getenv('FN_CALL', True))
API_BASE_URL = os.getenv('API_BASE_URL', None)
ADD_USER = str_to_bool(os.getenv('ADD_USER', False))

NON_FN_CALL = str_to_bool(os.getenv('NON_FN_CALL', False))

NOT_SUPPORT_SENDER = ["mistral", "groq"]

MUST_ADD_USER = ["deepseek/deepseek-reasoner", "o1-mini"]
NOT_SUPPORT_FN_CALL = ["o1-mini", "deepseek/deepseek-reasoner"]
NOT_USE_FN_CALL = ["deepseek/deepseek-chat"] + NOT_SUPPORT_FN_CALL

if EVAL_MODE:
    DEFAULT_LOG = False
