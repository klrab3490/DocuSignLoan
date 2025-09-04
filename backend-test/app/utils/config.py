# app/utils/config.py
"""
Configuration for the backend.
Includes Gemini API client and optional Tesseract path.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai  # Google Gemini API client

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# ---------------- File size limits ---------------- #
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ---------------- Gemini API Client ---------------- #
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # <-- store raw key
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set in .env")

client = genai.Client(api_key=GOOGLE_API_KEY)

# ---------------- Optional Tesseract ---------------- #
TESSERACT_CMD = os.getenv("TESSERACT_CMD")  # Windows path to tesseract.exe
