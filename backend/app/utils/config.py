import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Configure Gemini API
client = genai.Client(api_key=os.getenv("LLM_API"))
