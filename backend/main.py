import os
import uuid
from google import genai
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from google.genai import types
from typing import Optional, List
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Initialize FastAPI app
app = FastAPI()

# Configure Gemini API
client = genai.Client(api_key=os.getenv("LLM_API"))

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# In-memory job history
processing_jobs: dict[str, dict] = {}

class ExtractResponse(BaseModel):
    job_id: str
    text_content: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None

@app.post("/extract-content/", response_model=ExtractResponse)
async def extract_content_from_pdf(
    file: UploadFile = File(...),
    prompt: str = "Extract **all** text from the document exactly as it appears, preserving structure, spacing, and formatting as much as possible. Return only the raw extracted text without summaries or interpretations."
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    pdf_bytes = await file.read()

    # Size check
    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")

    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {"status": "processing", "result": None}

    try:
        # Send to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf"
                ),
                prompt
            ],
        )

        # Store result
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["result"] = response.text

        return ExtractResponse(job_id=job_id, text_content=response.text)

    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    job = processing_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job_id, **job)

@app.get("/status", response_model=List[JobStatusResponse])
async def get_all_statuses():
    return [
        JobStatusResponse(job_id=job_id, **data)
        for job_id, data in processing_jobs.items()
    ]
