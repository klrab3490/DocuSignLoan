import json
import os
from typing import Dict, Any

JOB_FILE = "jobs.json"


def save_jobs_to_file(processing_jobs: Dict[str, Any]) -> None:
    """Save jobs safely to a JSON file."""
    try:
        with open(JOB_FILE, "w", encoding="utf-8") as f:
            json.dump(processing_jobs, f, ensure_ascii=False, indent=2)
    except OSError as e:
        # Log or raise depending on your needs
        print(f"[ERROR] Failed to save jobs: {e}")


def load_jobs_from_file() -> Dict[str, Any]:
    """Load jobs from JSON file; return empty dict if missing or invalid."""
    if not os.path.exists(JOB_FILE):
        return {}

    try:
        with open(JOB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] Failed to load jobs: {e}")
        return {}
