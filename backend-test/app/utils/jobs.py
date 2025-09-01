import json
import os

job_file = "jobs.json"

def save_jobs_to_file(processing_jobs):
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(processing_jobs, f, ensure_ascii=False, indent=2)

def load_jobs_from_file():
    if os.path.exists(job_file):
        try:
            with open(job_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}
