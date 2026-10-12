"""
Configuration module for Company Knowledge Base RAG Chatbot.
Loads settings from environment variables or .env file with production defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project paths
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
MANIFEST_FILE = VECTORSTORE_DIR / "manifest.json"

# Automatically load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Ensure essential runtime directories exist
DOCUMENTS_DIR.mkdir(exist_ok=True, parents=True)
VECTORSTORE_DIR.mkdir(exist_ok=True, parents=True)

# Google Gemini API & Model Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# RAG Splitting & Retrieval Parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "4"))
SEARCH_TYPE = os.getenv("SEARCH_TYPE", "similarity")  # 'similarity' or 'mmr'
