"""
Configuration file for AI Co-worker Engine
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
PROMPTS_DIR = DATA_DIR / "prompts"

# Create directories if they don't exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Settings
LLM_MODEL = "claude-3-5-sonnet-20241022"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000

# RAG Settings
VECTOR_DB_PATH = str(BASE_DIR / "vector_store")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RETRIEVAL = 3

# Session Settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
SESSION_TTL = 86400  # 24 hours

# Director Settings
STUCK_LOOP_THRESHOLD = 3
SIMILARITY_THRESHOLD = 0.85

# Safety Settings
MAX_MESSAGE_LENGTH = 2000
PROFANITY_FILTER_ENABLED = True

# Security Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# CORS Settings
ALLOWED_ORIGINS = [
    "http://localhost:3000", # Frontend - React/Vue (NOT BUILD)
    "http://localhost:8000", # Current API
    "https://edtronaut.ai"
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")