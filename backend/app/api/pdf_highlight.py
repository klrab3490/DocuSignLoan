import os, re, fitz
from app.utils import load_jobs_from_file
from fastapi import APIRouter, HTTPException
import difflib

router = APIRouter()

UPLOADS_DIR = "uploads"

def find_phrase_coords(page, phrase: str, threshold: float = 0.5):
    """
    Find coordinates of a phrase by matching sentences with at least `threshold` similarity.
    Returns bounding box of the best match, else None.
    """

    blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, "text", block_no)
    phrase_norm = phrase.lower().strip()

    best_match = None
    best_score = 0

    for b in blocks:
        if len(b) < 5:
            continue
        block_text = b[4].lower().strip()
        score = difflib.SequenceMatcher(None, phrase_norm, block_text).ratio()
        if score >= threshold and score > best_score:
            best_match = b
            best_score = score

    if best_match:
        # Return bounding box for the best matching block
        return [(best_match[0], best_match[1], best_match[2], best_match[3])]
    return None

@router.get("/highlight/")
async def highlight_text(job_id: str, page_number: int, content: str):
    """
    Highlight a given content string on a specific page of a PDF.
    """
    jobs = load_jobs_from_file()
    job = jobs.get(job_id)
    
    # print(f"Job Details: {job}")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = os.path.join(UPLOADS_DIR, f"{job['filename']}")
    # print(f"File Path: {file_path}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    doc = fitz.open(file_path)
    # print(f"Total pages in PDF: {len(doc)}")
    if page_number < 1 or page_number > len(doc):
        raise HTTPException(status_code=400, detail="Invalid page number")

    page = doc[page_number - 1]
    # print(f"Page where content is located: {page_number} and {page}")
    # print(f"Content on page {page_number}:")
    
    coords = find_phrase_coords(page, content)
    if not coords:
        raise HTTPException(status_code=404, detail="Text not found in PDF")

    # Create a single bounding box around the phrase
    rect = fitz.Rect(
        min(x0 for x0, _, _, _ in coords),
        min(y0 for _, y0, _, _ in coords),
        max(x1 for _, _, x1, _ in coords),
        max(y1 for _, _, _, y1 in coords),
    )

    # Add highlight
    highlight = page.add_highlight_annot(rect)
    highlight.update()

    # Save highlighted PDF
    output_path = file_path.replace(".pdf", "_highlighted.pdf")
    doc.save(output_path)

    return {"message": "Highlight added", "output_file": output_path}
