from typing import Dict, List, Optional
from app.utils import load_jobs_from_file
from pydantic import BaseModel, RootModel
from fastapi import APIRouter, HTTPException

router = APIRouter()


class ExtractedField(BaseModel):
    value: Optional[str] = None
    page_number: int

class JobResult(RootModel):
    root: Dict[str, Dict[str, ExtractedField]]

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    result: Optional[JobResult] = None
    pages: Optional[Dict[int, str]] = None

# Route: /jobs/{job_id}
@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status and details of a specific job.
    """
    data = load_jobs_from_file()
    job = data.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        filename=job.get("filename", ""),
        result=job.get("result"),
        pages=job.get("pages"),
    )


class JobSummary(BaseModel):
    job_id: str
    status: str
    filename: str

# Route: /status
@router.get("/status", response_model=List[JobSummary])
async def get_all_jobs():
    """
    Get statuses of all jobs.
    """
    data = load_jobs_from_file()
    return [
        JobSummary(
            job_id=job_id,
            status=job["status"],
            filename=job["filename"]
        )
        for job_id, job in data.items()
    ]
