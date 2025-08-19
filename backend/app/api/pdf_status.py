from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.utils import load_jobs_from_file

router = APIRouter()

class PageResult(BaseModel):
    page_number: int
    extracted_data: Dict[str, Any]  # allows nested dicts inside

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    result: Optional[List[PageResult]] = None  # list of structured results
    pages: Optional[Dict[int, str]] = None  # page_number → text


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
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


@router.get("/status", response_model=list[str])
async def get_all_statuses():
    data = load_jobs_from_file()
    return list(data.keys())
