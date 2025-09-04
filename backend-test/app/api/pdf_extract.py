import uuid
import hashlib
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
    pages: Dict[str, str]   # use str keys for JSON consistency
    full_text: str

def file_hash(content: bytes) -> str:
    """Generate sha256 hash for deduplication."""
    return hashlib.sha256(content).hexdigest()

@router.post("/extract-and-format/")
async def extract_and_format_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    # Read content safely
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")
    file.file.seek(0)

    # Save file permanently
    file_path, temp_file_path = await save_file_permanent(file)

    # Job management - use file hash instead of only filename
    file_digest = file_hash(content)
    original_filename = file.filename
    existing_job_id = next(
        (jid for jid, job in processing_jobs.items() if job.get("file_hash") == file_digest),
        None,
    )

    if existing_job_id:
        job_id = existing_job_id
        processing_jobs[job_id].update({
            "status": "processing",
            "result": None,
            "filename": original_filename,
            "pages": {},
            "file_path": file_path,
        })
    else:
        job_id = str(uuid.uuid4())
        processing_jobs[job_id] = {
            "status": "processing",
            "result": None,
            "filename": original_filename,
            "file_hash": file_digest,
            "pages": {},
            "file_path": file_path,
        }
    save_jobs_to_file(processing_jobs)

    try:
        run = run_pipeline_on_pdf(temp_file_path)

        processing_jobs[job_id].update({
            "status": "completed",
            "result": run["schema"],
            "pages": run["pages"],
        })
        save_jobs_to_file(processing_jobs)

        await delete_temp_file(file)

        return ExtractResponse(
            job_id=job_id,
            result=run["schema"],
            pages={str(k): v for k, v in run["pages"].items()},  # enforce str keys
            full_text=run["full_text"]
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # debug log

        processing_jobs[job_id].update({
            "status": "failed",
            "result": str(e),
        })
        save_jobs_to_file(processing_jobs)
        await delete_temp_file(file)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
