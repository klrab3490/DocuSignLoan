import os, shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
UPLOAD_DIR_temp = "uploads/temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR_temp, exist_ok=True)

# Function to save a file permanently and temporarily
async def save_file_permanent(file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    temp_file_path = os.path.join(UPLOAD_DIR_temp, file.filename)

    if os.path.exists(file_path) and os.path.exists(temp_file_path):
        return [file_path, temp_file_path]

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.seek(0)  # Reset file pointer to the beginning
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return [file_path, temp_file_path]

# Function to delete a temporary file
async def delete_temp_file(file: UploadFile) -> None:
    temp_file_path = os.path.join(UPLOAD_DIR_temp, file.filename)
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
