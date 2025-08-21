import os
import fitz  # PyMuPDF
from app.utils import load_jobs_from_file
from fastapi import APIRouter, HTTPException

router = APIRouter()

UPLOADS_DIR = "uploads"

def find_phrase_coords(page, phrase: str):
    """
    Find coordinates of a multi-word phrase on a PDF page.
    Returns list of bounding boxes if found, else None.
    """
    words = page.get_text("words")  # list of (x0, y0, x1, y1, "word")
    phrase_tokens = phrase.split()  # split by spaces → ["27", "November", "2023"]
    print(f"Searching for phrase: {phrase_tokens}")

    for i in range(len(words) - len(phrase_tokens) + 1):
        window = [w[4] for w in words[i:i + len(phrase_tokens)]]
        print(f"Comparing window: {window} with phrase tokens: {phrase_tokens}")
        if window == phrase_tokens:
            print(f"Found phrase at index {i}: {window}")
            coords = [(w[0], w[1], w[2], w[3]) for w in words[i:i + len(phrase_tokens)]]
            return coords
        # If not exact match, check if any two words from phrase_tokens are found near each other
        for j in range(len(phrase_tokens) - 1):
            if window[j] == phrase_tokens[j] and window[j + 1] == phrase_tokens[j + 1]:
                print(f"Found two words near at index {i + j}: {window[j]}, {window[j + 1]}")
                coords = [(words[i + j][0], words[i + j][1], words[i + j][2], words[i + j][3]),
                      (words[i + j + 1][0], words[i + j + 1][1], words[i + j + 1][2], words[i + j + 1][3])]
                return coords
    return None

@router.get("/pdf/highlight/")
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
    page_text = page.get_text()

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
    doc.save(output_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)

    return {"message": "Highlight added", "output_file": output_path}
