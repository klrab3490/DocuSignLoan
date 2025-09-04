import json
import re
from typing import Dict, Any, List

from langchain.schema import HumanMessage, SystemMessage
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


# --- Instructions ---
SCHEMA_INSTRUCTIONS = """
Extract information into the following strict JSON schema. 
For each category, return its fields as key-value pairs.
Each field must be represented as an object with: { 'value': str, 'page_number': int }.
If a field is not present in the document, set value=null and page_number=null.
Respond with ONLY JSON, no surrounding text or markdown.
Schema:
{schema}
""".strip()


# --- Runner ---
def run_pipeline_on_pdf(pdf_path: str, chunk_size: int = 30) -> Dict[str, Any]:
    """
    Conversation-style pipeline:
      1. Extract text per page with OCR fallback.
      2. Send chunks sequentially in the same conversation.
      3. Ask once at the end for final schema.
      4. Return pages + full_text + schema.
    """
    # Step 1: OCR per page
    page_texts: Dict[int, str] = extract_text_with_ocr(pdf_path)

    # Step 2: Concatenate all text for reference
    full_text = "\n\n".join(
        [f"--- Page {i} ---\n{text}" for i, text in page_texts.items()]
    )

    # Step 3: Build conversation
    schema_text = json.dumps(MASTER_SCHEMA, indent=2)

    messages: List[Any] = [
        SystemMessage(content="You are a strict JSON extractor."),
        HumanMessage(content=SCHEMA_INSTRUCTIONS.replace("{schema}", schema_text)),
    ]

    # Add chunks as conversation turns
    page_numbers = sorted(page_texts.keys())
    chunks = [
        page_numbers[i:i + chunk_size]
        for i in range(0, len(page_numbers), chunk_size)
    ]

    for idx, chunk in enumerate(chunks, start=1):
        chunk_text = "\n".join(f"--- Page {i} ---\n{page_texts[i]}" for i in chunk)
        messages.append(HumanMessage(content=f"Here is chunk {idx}:\n{chunk_text}"))

    # Final instruction: output schema
    messages.append(HumanMessage(content="Now return the final schema as valid JSON."))

    # Step 4: Run Gemini once with full conversation
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
    resp = model.invoke(messages)
    raw = getattr(resp, "content", str(resp))

    try:
        parsed = safe_json_parse(raw)
        schema = ensure_schema_keys(parsed)
    except Exception:
        schema = ensure_schema_keys({})

    # Step 5: Return combined result
    return {
        "pages": page_texts,
        "full_text": full_text,
        "schema": schema,
    }
