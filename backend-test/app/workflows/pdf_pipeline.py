# app/workflows/pdf_pipeline.py
"""
Hybrid PDF Pipeline:
 - Step 1: OCR per page (guarantees full text extraction).
 - Step 2: Concatenate all page texts.
 - Step 3: Call Gemini once with the full document to extract schema.
 - Step 4: Return {pages, full_text, schema}.
"""

import json
import re
from typing import Dict, Any

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.utils import extract_text_with_ocr, ensure_schema_keys, MASTER_SCHEMA, GOOGLE_API_KEY


# --- Helper: safe JSON parser ---
def safe_json_parse(raw_text: str) -> Any:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        fix_prompt = f"""
        The following text is intended to be JSON but is invalid.
        Fix it and return ONLY valid JSON with no extra commentary:
        {raw_text}
        """
        fix_response = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY
        ).invoke([HumanMessage(content=fix_prompt)])
        
        fixed_text = re.sub(
            r"^```json\s*|\s*```$",
            "",
            getattr(fix_response, "content", str(fix_response)).strip(),
            flags=re.MULTILINE
        ).strip()
        return json.loads(fixed_text)


# --- Prompt ---
SCHEMA_INSTRUCTIONS = """
Extract information into the following strict JSON schema. 
For each category, return its fields as key-value pairs.
Each field must be represented as an object with: { 'value': str, 'page_number': int }.
If a field is not present in the document, set value=null and page_number=null.
Respond with ONLY JSON, no surrounding text or markdown.
Schema:
{schema}
""".strip()


def build_prompt_for_full_doc(full_text: str, page_texts: Dict[int, str]) -> str:
    schema_text = json.dumps(MASTER_SCHEMA, indent=2)
    pages_text = "\n".join(
        f"--- PAGE {i} ---\n{text}" for i, text in page_texts.items()
    )
    return (
        "You are a strict JSON formatter. "
        "Return ONLY valid JSON with no markdown fences or commentary.\n\n"
        f"{SCHEMA_INSTRUCTIONS.replace('{schema}', schema_text)}\n\n"
        "Document text with page numbers:\n"
        f"{pages_text}"
    )


# --- Runner ---
def run_pipeline_on_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Hybrid pipeline:
      1. Extract text per page with OCR fallback.
      2. Concatenate into full_text.
      3. Run Gemini once to extract schema.
      4. Return pages + full_text + schema.
    """
    # Step 1: OCR per page
    page_texts: Dict[int, str] = extract_text_with_ocr(pdf_path)

    # Step 2: Concatenate
    full_text = "\n\n".join(
        [f"--- Page {i} ---\n{text}" for i, text in page_texts.items()]
    )

    # Step 3: Run Gemini
    # print(f"Running Gemini... {GOOGLE_API_KEY}")
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
    prompt = build_prompt_for_full_doc(full_text, page_texts)
    resp = model.invoke([HumanMessage(content=prompt)])
    raw = getattr(resp, "content", str(resp))

    # print("\n=== RAW GEMINI RESPONSE (first 500 chars) ===")
    # print(raw[:500], "...\n")

    parsed = safe_json_parse(raw)
    # print(f"=== PARSED GEMINI RESPONSE ===\n{json.dumps(parsed, indent=2)}\n")
    schema = ensure_schema_keys(parsed)
    if not schema:
        print("Warning: Failed to parse Gemini response as valid schema.")
        schema = ensure_schema_keys({})

    # Step 4: Return combined result
    return {
        "pages": page_texts,
        "full_text": full_text,
        "schema": schema,
    }
