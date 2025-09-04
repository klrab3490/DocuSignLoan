from typing import Dict, List, Optional
from app.utils import load_jobs_from_file
from pydantic import BaseModel, RootModel
from fastapi import APIRouter, HTTPException

router = APIRouter()


# ----------------------------
# Models
# ----------------------------

class ExtractedField(BaseModel):
    value: Optional[str] = None
    page_number: Optional[int] = None


class JobResult(RootModel[Dict[str, Dict[str, ExtractedField]]]):
    """Root model for the job extraction result."""
    pass


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    file_path: Optional[str] = None
    result: Optional[JobResult] = None
    pages: Optional[Dict[int, str]] = None


class JobSummary(BaseModel):
    job_id: str
    status: str
    filename: str


# ----------------------------
# Routes
# ----------------------------

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Fetch the status of a single job by job_id."""
    data = load_jobs_from_file()
    job = data.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        filename=job.get("filename", ""),
        file_path=job.get("file_path"),
        result=job.get("result"),
        pages=job.get("pages"),
    )


@router.get("/status", response_model=List[JobSummary])
async def get_all_jobs():
    """Fetch a list of all jobs with minimal details."""
    data = load_jobs_from_file()
    return [
        JobSummary(
            job_id=job_id,
            status=job.get("status", "unknown"),
            filename=job.get("filename", "")
        )
        for job_id, job in data.items()
    ]
