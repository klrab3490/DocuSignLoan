import os
import re
import fitz
import uuid
import json
from google import genai
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from google.genai import types
from typing import Optional, List, Union
from fastapi import FastAPI, File, UploadFile, HTTPException

# Save to a JSON File
job_file = "jobs.json"

def save_jobs_to_file():
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(processing_jobs, f, ensure_ascii=False, indent=2)

def load_jobs_from_file():
    if os.path.exists(job_file):
        with open(job_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

processing_jobs = load_jobs_from_file()

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
    filename: str
    result: Optional[Union[str, dict]] = None


@app.post("/extract-and-format/", response_model=ExtractResponse)
async def extract_and_format_pdf(
    file: UploadFile = File(...),
    format_instructions: str = "Extract parties, agreement name, agreement date, and clauses into JSON format."
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")

    original_filename = file.filename

    # Check if filename already exists
    existing_job_id = None
    for jid, job in processing_jobs.items():
        if job.get("filename") == original_filename:
            existing_job_id = jid
            break

    # If exists → reuse job ID
    if existing_job_id:
        job_id = existing_job_id
        processing_jobs[job_id]["status"] = "processing"
        processing_jobs[job_id]["result"] = None
    else:
        job_id = str(uuid.uuid4())
        processing_jobs[job_id] = {
            "status": "processing",
            "result": None,
            "filename": original_filename
        }

    save_jobs_to_file()  # Save state

    try:
        # Extract text locally
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = "\n".join(page.get_text("text") for page in doc)

        # Send to LLM
        prompt = f"""
        You are a strict JSON formatter. Return ONLY valid JSON with no markdown fences or extra commentary.
        {format_instructions}

        Document text:
        {full_text}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
        )

        raw_output = response.text.strip()
        clean_output = re.sub(r"^```json\s*|\s*```$", "", raw_output, flags=re.MULTILINE).strip()
        parsed_json = json.loads(clean_output)

        # Update job result
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["result"] = parsed_json
        save_jobs_to_file()

        return ExtractResponse(job_id=job_id, text_content=json.dumps(parsed_json, ensure_ascii=False))

    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        save_jobs_to_file()
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")



@app.post("/extract-content/", response_model=ExtractResponse)
async def extract_content_from_pdf(
    file: UploadFile = File(...),
    prompt: str = "Extract **all** text from the document exactly as it appears, preserving structure, spacing, and formatting as much as possible. Return only the raw extracted text without summaries or interpretations."
):
    """
    1. Upload file
    2. Send the file to Gemini for processing
    3. Return the extracted content
    """
    
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
    """
    Get the status of a specific job.
    """
    data = load_jobs_from_file()
    job = data.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job_id, **job)

@app.get("/status", response_model=List[JobStatusResponse])
async def get_all_statuses():
    """
    Get the status of all jobs.
    """
    data = load_jobs_from_file()
    return [
        JobStatusResponse(job_id=job_id, **data)
        for job_id, data in data.items()
    ]
