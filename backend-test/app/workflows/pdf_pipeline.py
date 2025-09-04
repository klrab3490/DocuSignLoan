import json
import re
import copy
from typing import Dict, Any
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.utils import extract_text_with_ocr, ensure_schema_keys, MASTER_SCHEMA, GOOGLE_API_KEY


def safe_json_parse(raw_text: str, retries: int = 2) -> Dict[str, Any]:
    """
    Safely parse JSON. If invalid, retries a few times by asking Gemini to repair.
    Strips markdown fences and repairs minor formatting.
    """
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        if retries <= 0:
            raise ValueError(f"Unable to parse JSON after retries. Raw text:\n{raw_text[:500]}...")

        # Ask Gemini to repair
        fix_prompt = f"""
        The following text is intended to be JSON but is invalid.
        Fix it and return ONLY valid JSON with no extra commentary:
        {raw_text}
        """
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY
        )
        try:
            resp = model.invoke([HumanMessage(content=fix_prompt)])
            fixed_text = getattr(resp, "content", str(resp)).strip()

            # Strip common markdown/code fences
            fixed_text = re.sub(r"^```(json)?\s*|\s*```$", "", fixed_text, flags=re.MULTILINE).strip()

            return safe_json_parse(fixed_text, retries=retries - 1)
        except Exception as e:
            raise ValueError(f"Gemini failed to fix JSON: {e}")


def build_batch_prompt(text: str) -> str:
    """
    Build a JSON-extraction prompt for Gemini using the MASTER_SCHEMA.
    """
    schema_text = json.dumps(MASTER_SCHEMA, indent=2)
    return (
        "You are a strict JSON formatter. "
        "Return ONLY valid JSON with no markdown fences or commentary. "
        "Extract every possible field even if unclear; "
        "guess sensibly but never omit required keys.\n\n"
        f"Extract information into the following strict JSON schema:\n{schema_text}\n\n"
        f"Document text:\n{text}"
    )


def merge_schemas(page_schemas: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple page-level schemas into a single schema.
    Strategy: for each field, prefer the first non-null occurrence across pages.
    """
    from app.utils.merge_utils import _take_first_non_null
    merged = ensure_schema_keys({})
    for _, schema in page_schemas.items():
        normalized = ensure_schema_keys(schema)
        for section, fields in normalized.items():
            for key, obj in fields.items():
                merged[section][key] = _take_first_non_null(merged[section].get(key), obj)
    return merged


def run_pipeline_on_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Run the full extraction pipeline on a PDF:
    1. OCR text extraction
    2. Batch Gemini JSON extraction (per-page schemas inside one response)
    3. Schema merging
    """
    pages = extract_text_with_ocr(pdf_path)

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY
    )

    page_results: Dict[int, Dict[str, Any]] = {}

    # ---- Batch pages in groups of 3 (adjust batch size as needed) ----
    batch_size = 3
    page_items = list(pages.items())

    for i in range(0, len(page_items), batch_size):
        batch = page_items[i:i + batch_size]

        combined_text = "\n\n".join(
            f"--- PAGE {num} ---\n{text}" for num, text in batch
        )

        schema_text = json.dumps(MASTER_SCHEMA, indent=2)
        prompt = (
            "You are a strict JSON formatter. "
            "Return ONLY valid JSON with no markdown fences or commentary. "
            "Extract every possible field even if unclear; "
            "guess sensibly but never omit required keys.\n\n"
            "For each page, return results in a dictionary keyed by the page number.\n"
            "Example:\n"
            "{\n"
            "  \"1\": { ...schema... },\n"
            "  \"2\": { ...schema... }\n"
            "}\n\n"
            f"Strict JSON schema for each page:\n{schema_text}\n\n"
            f"Document text:\n{combined_text}"
        )

        try:
            resp = model.invoke([HumanMessage(content=prompt)])
            raw_output = getattr(resp, "content", str(resp))
            parsed = safe_json_parse(raw_output)

            # Assign results page by page (fallback if Gemini skipped a page)
            for num, _ in batch:
                page_schema = parsed.get(str(num), {})
                page_results[num] = ensure_schema_keys(page_schema)

        except Exception as e:
            print(f"[Warning] Failed to process batch {i//batch_size+1}: {e}")
            for num, _ in batch:
                page_results[num] = ensure_schema_keys({})

    merged_schema = merge_schemas(page_results)
    final_schema = ensure_schema_keys(merged_schema)

    full_text = "\n\n".join(
        [f"--- Page {i} ---\n{text}" for i, text in pages.items()]
    )

    return {
        "pages": pages,
        "full_text": full_text,
        "schema": final_schema,
    }
