import uuid
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.utils import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    save_file_permanent,
    delete_temp_file,
    load_jobs_from_file,
    save_jobs_to_file,
)
from app.workflows import run_pipeline_on_pdf

router = APIRouter()
processing_jobs: Dict[str, Any] = load_jobs_from_file()

class ExtractResponse(BaseModel):
    job_id: str
    result: Dict[str, Any]
    pages: Dict[int, str]
    full_text: str

@router.post("/extract-and-format/")
async def extract_and_format_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    [file_path, temp_file_path] = await save_file_permanent(file)

    # Check size
    file.file.seek(0)
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")
    file.file.seek(0)

    # Job management
    original_filename = file.filename
    existing_job_id = next(
        (jid for jid, job in processing_jobs.items() if job.get("filename") == original_filename),
        None,
    )

    if existing_job_id:
        job_id = existing_job_id
        processing_jobs[job_id]["status"] = "processing"
        processing_jobs[job_id]["result"] = None
    else:
        job_id = str(uuid.uuid4())
        processing_jobs[job_id] = {
            "status": "processing",
            "result": None,
            "filename": original_filename,
            "pages": {},
            "file_path": file_path,
        }
    save_jobs_to_file(processing_jobs)

    try:
        run = run_pipeline_on_pdf(temp_file_path)

        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["result"] = run["schema"]
        processing_jobs[job_id]["pages"] = run["pages"]
        save_jobs_to_file(processing_jobs)

        await delete_temp_file(file)

        return ExtractResponse(
            job_id=job_id,
            result=run["schema"],
            pages=run["pages"],
            full_text=run["full_text"]
        )

    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        save_jobs_to_file(processing_jobs)
        await delete_temp_file(file)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
