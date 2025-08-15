import re
import uuid
import json
import fitz
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from google.genai import types

from app.utils import save_jobs_to_file, load_jobs_from_file, client, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB

router = APIRouter()
processing_jobs = load_jobs_from_file()

class ExtractResponse(BaseModel):
    job_id: str
    text_content: str  # JSON string
    pages: Dict[int, str]  # page_number → page text


def safe_json_parse(raw_text: str) -> Any:
    """Try to parse JSON, if fails, ask Gemini to fix it."""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        fix_prompt = f"""
        The following text is intended to be JSON but is invalid.
        Fix it and return ONLY valid JSON with no extra commentary:
        {raw_text}
        """
        fix_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[fix_prompt],
        )
        fixed_text = re.sub(
            r"^```json\s*|\s*```$",
            "",
            fix_response.text.strip(),
            flags=re.MULTILINE
        ).strip()
        return json.loads(fixed_text)


@router.post("/extract-and-format/", response_model=ExtractResponse)
async def extract_and_format_pdf(
    file: UploadFile = File(...),
    format_instructions: str = (
        "For each page, extract parties, agreement name, agreement date, and clauses. "
        "Output as a JSON array where each item has: "
        "{ 'page_number': int, 'extracted_data': {...fields...} }."
    )
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB} MB.")

    original_filename = file.filename
    existing_job_id = next((jid for jid, job in processing_jobs.items() if job.get("filename") == original_filename), None)

    if existing_job_id:
        job_id = existing_job_id
        processing_jobs[job_id]["status"] = "processing"
        processing_jobs[job_id]["result"] = None
    else:
        job_id = str(uuid.uuid4())
        processing_jobs[job_id] = {
            "status": "processing",
            "result": None,
            "filename": original_filename,
            "pages": {}
        }

    save_jobs_to_file(processing_jobs)

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Extract text per page
        page_texts = {}
        for page_number in range(len(doc)):
            page_texts[page_number + 1] = doc[page_number].get_text("text")

        # Build prompt with page-specific text
        full_text_with_pages = "\n".join(
            f"--- PAGE {page_num} ---\n{text}"
            for page_num, text in page_texts.items()
        )

        prompt = f"""
        You are a strict JSON formatter. Return ONLY valid JSON with no markdown fences or extra commentary.
        {format_instructions}

        Document text with page numbers:
        {full_text_with_pages}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
        )

        raw_output = response.text.strip()
        clean_output = re.sub(
            r"^```json\s*|\s*```$",
            "",
            raw_output,
            flags=re.MULTILINE
        ).strip()

        parsed_json = safe_json_parse(clean_output)

        # Save job result & pages
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["result"] = parsed_json
        processing_jobs[job_id]["pages"] = page_texts
        save_jobs_to_file(processing_jobs)

        return ExtractResponse(
            job_id=job_id,
            text_content=json.dumps(parsed_json, ensure_ascii=False),
            pages=page_texts
        )

    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        save_jobs_to_file(processing_jobs)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
