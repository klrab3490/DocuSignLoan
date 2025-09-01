from typing import Dict, List, Optional
from pydantic import BaseModel, RootModel
from fastapi import APIRouter, HTTPException
from app.utils import load_jobs_from_file

router = APIRouter()


class ExtractedField(BaseModel):
    value: Optional[str] = None
    page_number: Optional[int] = None


class JobResult(RootModel):
    root: Dict[str, Dict[str, ExtractedField]]


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    file_path: str | None = None
    result: Optional[JobResult] = None
    pages: Optional[Dict[int, str]] = None


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
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


class JobSummary(BaseModel):
    job_id: str
    status: str
    filename: str


@router.get("/status", response_model=List[JobSummary])
async def get_all_jobs():
    data = load_jobs_from_file()
    return [
        JobSummary(job_id=job_id, status=job["status"], filename=job["filename"])
        for job_id, job in data.items()
    ]
