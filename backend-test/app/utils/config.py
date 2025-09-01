import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Configure Gemini API
client = genai.Client(api_key=os.getenv("LLM_API"))

# Optional: Tesseract binary path (Windows)
GOOGLE_API_KEY = os.getenv("LLM_API")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
