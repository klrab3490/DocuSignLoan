import os

def sanitize_filename(filename: str, allowed_ext=".pdf") -> str:
    if not filename.lower().endswith(allowed_ext) or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")
    return os.path.basename(filename)
