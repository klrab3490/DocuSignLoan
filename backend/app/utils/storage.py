import os, shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_file_permanent(file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    if os.path.exists(file_path):
        return file_path

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path
