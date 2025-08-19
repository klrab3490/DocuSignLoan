from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, RootModel
from app.utils import load_jobs_from_file

router = APIRouter()


class ExtractedField(BaseModel):
    value: Optional[str]
    page_number: Optional[int]


# Each category is a dict of fields → ExtractedField
class ExtractedCategory(RootModel[Dict[str, ExtractedField]]):
    pass


class ExtractedResult(BaseModel):
    dates: Dict[str, ExtractedField]
    general: Dict[str, ExtractedField]
    definitions: Dict[str, ExtractedField]
    credit_facilities: Dict[str, ExtractedField]
    covenants: Dict[str, ExtractedField]
    representations_and_warranties: Dict[str, ExtractedField]
    defaults: Dict[str, ExtractedField]
    miscellaneous: Dict[str, ExtractedField]


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    result: Optional[ExtractedResult] = None
    pages: Optional[Dict[int, str]] = None


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


@router.get("/status", response_model=List[str])
async def get_all_statuses():
    data = load_jobs_from_file()
    return list(data.keys())
