from fastapi import APIRouter, HTTPException
from typing import Optional, Union, List, Dict
from pydantic import BaseModel
from app.utils import load_jobs_from_file

router = APIRouter()

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    result: Optional[Union[str, dict]] = None
    pages: Optional[Dict[int, str]] = None  # page_number → text

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    data = load_jobs_from_file()
    job = data.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job_id, **job)

@router.get("/status", response_model=List[JobStatusResponse])
async def get_all_statuses():
    data = load_jobs_from_file()
    return [JobStatusResponse(job_id=job_id, **data) for job_id, data in data.items()]
