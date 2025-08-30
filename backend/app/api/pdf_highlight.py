import os, difflib, fitz
from fastapi import APIRouter, HTTPException
from app.utils import client, load_jobs_from_file

router = APIRouter()

UPLOADS_DIR = "uploads"

def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace for comparison."""
    return " ".join(text.lower().split())

def fetch_passage_with_ai(page_text: str, query: str) -> str:
    prompt = f"""
    You are given the following page text:

    {page_text}

    Find the passage (sentence or paragraph) that best matches:
    "{query}"

    Return ONLY the passage text.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
    )
    fetched_passage = response.text.strip()
    # print(f"Fetched Passage: {fetched_passage}")
    return fetched_passage

def find_phrase_coords_from_ai(page, ai_passage: str, query: str, threshold: float = 0.6):
    """
    Given AI's extracted passage and original query, find matching blocks in PDF.
    Works even if the paragraph is split across multiple blocks.
    """
    blocks = page.get_text("blocks")  # (x0, y0, x1, y1, "text", block_no)
    ai_norm = normalize_text(ai_passage)
    query_norm = normalize_text(query)

    matched_coords = []

    # Pass 1: fuzzy compare each block against AI passage
    for b in blocks:
        if len(b) < 5:
            continue
        block_text = b[4]
        block_norm = normalize_text(block_text)

        score = difflib.SequenceMatcher(None, ai_norm, block_norm).ratio()
        if score > threshold or ai_norm in block_norm or block_norm in ai_norm:
            matched_coords.append((b[0], b[1], b[2], b[3]))

    # Pass 2: if nothing found, try using query as anchor
    if not matched_coords:
        for b in blocks:
            if len(b) < 5:
                continue
            block_text = normalize_text(b[4])
            if query_norm and query_norm in block_text:
                matched_coords.append((b[0], b[1], b[2], b[3]))

    if not matched_coords:
        return None

    # Sort and return block coords (top-to-bottom, left-to-right)
    matched_coords = sorted(matched_coords, key=lambda r: (r[1], r[0]))
    return matched_coords

@router.get("/highlight/")
async def highlight_text(job_id: str, page_number: int, query: str):
    """
    Highlight the passage that AI finds for a given query string.
    """
    print(f"Job Request: Highlighting for job {job_id}, page {page_number}, query: {query}")

    jobs = load_jobs_from_file()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = os.path.join(UPLOADS_DIR, f"{job['filename']}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    doc = fitz.open(file_path)
    if page_number < 1 or page_number > len(doc):
        raise HTTPException(status_code=400, detail="Invalid page number")

    page = doc[page_number - 1]

    # Extract text from page
    page_text = page.get_text("text")

    # Step 1: Ask AI for best passage
    ai_passage = fetch_passage_with_ai(page_text, query)

    # Step 2: Map passage to PDF coords
    coords = find_phrase_coords_from_ai(page, ai_passage, query)
    if not coords:
        raise HTTPException(status_code=404, detail="Passage not found in PDF")

    # Add highlight for each block instead of one giant rectangle
    for (x0, y0, x1, y1) in coords:
        rect = fitz.Rect(x0, y0, x1, y1)
        highlight = page.add_highlight_annot(rect)
        highlight.update()


    output_path = file_path.replace(".pdf", "_highlighted.pdf")
    doc.save(output_path)

    return {"message": "Highlight added", "output_file": output_path}
