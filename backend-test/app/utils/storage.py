# app/utils/file_utils.py
import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
UPLOAD_DIR_TEMP = os.path.join(UPLOAD_DIR, "temp")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR_TEMP, exist_ok=True)


async def save_file_permanent(file: UploadFile) -> list[str]:
    """
    Save uploaded file both permanently and temporarily.
    
    Returns:
        [permanent_path, temp_path]
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    temp_file_path = os.path.join(UPLOAD_DIR_TEMP, file.filename)

    # Avoid overwriting if both exist
    if os.path.exists(file_path) and os.path.exists(temp_file_path):
        return [file_path, temp_file_path]

    # Save permanent copy
    with open(file_path, "wb") as f:
        file.file.seek(0)
        shutil.copyfileobj(file.file, f)

    # Save temp copy
    file.file.seek(0)
    with open(temp_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Reset file pointer for further usage
    file.file.seek(0)
    return [file_path, temp_file_path]


async def delete_temp_file(file: UploadFile) -> None:
    """
    Delete the temporary copy of the uploaded file.
    """
    print(f"Deleting temporary file: {file.filename}")
    temp_file_path = os.path.join(UPLOAD_DIR_TEMP, file.filename)
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
