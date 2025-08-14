import re
import uuid
import json
import fitz
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from google.genai import types

from app.utils import save_jobs_to_file, load_jobs_from_file, client, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB

router = APIRouter()
processing_jobs = load_jobs_from_file()

class ExtractResponse(BaseModel):
    job_id: str
    text_content: str

@router.post("/extract-and-format/", response_model=ExtractResponse)
async def extract_and_format_pdf(
    file: UploadFile = File(...),
    format_instructions: str = "Extract parties, agreement name, agreement date, and clauses into JSON format."
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")

    original_filename = file.filename
    existing_job_id = next((jid for jid, job in processing_jobs.items() if job.get("filename") == original_filename), None)

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

    save_jobs_to_file(processing_jobs)

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = "\n".join(page.get_text("text") for page in doc)

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

        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["result"] = parsed_json
        save_jobs_to_file(processing_jobs)

        return ExtractResponse(job_id=job_id, text_content=json.dumps(parsed_json, ensure_ascii=False))

    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        save_jobs_to_file(processing_jobs)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

@router.post("/extract-content/", response_model=ExtractResponse)
async def extract_content_from_pdf(
    file: UploadFile = File(...),
    prompt: str = "Extract **all** text from the document exactly as it appears, preserving structure, spacing, and formatting as much as possible. Return only the raw extracted text without summaries or interpretations."
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")

    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {"status": "processing", "result": None}

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                prompt
            ],
        )

        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["result"] = response.text
        return ExtractResponse(job_id=job_id, text_content=response.text)

    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
