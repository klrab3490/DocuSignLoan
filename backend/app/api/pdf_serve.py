import os
from app.utils import sanitize_filename
from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException

router = APIRouter()
UPLOAD_DIR = "uploads"

@router.get("/file/{filename}")
async def get_pdf(filename: str):
    try:
        safe_filename = sanitize_filename(filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    print(file_path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=safe_filename)
