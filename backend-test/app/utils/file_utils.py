import os
import re

def sanitize_filename(filename: str, allowed_ext: str = ".pdf") -> str:
    """
    Ensure a safe filename with only the allowed extension.
    
    - Blocks path traversal (`../`, `\`, `/`)
    - Normalizes whitespace
    - Removes unsafe characters
    """
    if not filename:
        raise ValueError("Filename is empty")

    # Extract only the base name (removes path parts if present)
    safe_name = os.path.basename(filename.strip())

    # Validate extension
    if not safe_name.lower().endswith(allowed_ext.lower()):
        raise ValueError(f"Invalid file type. Only {allowed_ext} allowed.")

    # Remove dangerous characters (keep alphanumeric, dash, underscore, dot, space)
    safe_name = re.sub(r"[^a-zA-Z0-9._ -]", "_", safe_name)

    return safe_name
