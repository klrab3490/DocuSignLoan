import json
import re
import asyncio
import logging
from typing import Dict, Any, List
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.utils import extract_text_with_ocr, ensure_schema_keys, MASTER_SCHEMA, GOOGLE_API_KEY

# -----------------------------
# Setup logging
# -----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def safe_json_parse(raw_text: str, retries: int = 2) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        if retries <= 0:
            raise ValueError(f"Unable to parse JSON after retries. Raw text:\n{raw_text[:500]}...")

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
            fixed_text = re.sub(r"^```(json)?\s*|\s*```$", "", fixed_text, flags=re.MULTILINE).strip()
            return safe_json_parse(fixed_text, retries=retries - 1)
        except Exception as e:
            raise ValueError(f"Gemini failed to fix JSON: {e}")


def merge_schemas(page_schemas: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    from app.utils.merge_utils import _take_first_non_null
    merged = ensure_schema_keys({})
    for _, schema in page_schemas.items():
        normalized = ensure_schema_keys(schema)
        for section, fields in normalized.items():
            for key, obj in fields.items():
                merged[section][key] = _take_first_non_null(merged[section].get(key), obj)
    return merged


async def process_batch(model, batch, schema_text, batch_id: int):
    """Process a batch of pages asynchronously"""
    combined_text = "\n\n".join(f"--- PAGE {num} ---\n{text}" for num, text in batch)

    prompt = (
        "You are a strict JSON formatter. "
        "Return ONLY valid JSON with no markdown fences or commentary. "
        "Extract every possible field even if unclear; "
        "guess sensibly but never omit required keys.\n\n"
        "For each page, return results in a dictionary keyed by the page number.\n"
        f"Strict JSON schema for each page:\n{schema_text}\n\n"
        f"Document text:\n{combined_text}"
    )

    page_nums = [num for num, _ in batch]
    logger.info(f"[BATCH {batch_id}] Starting pages {page_nums}")

    try:
        resp = await model.ainvoke([HumanMessage(content=prompt)])
        raw_output = getattr(resp, "content", str(resp))
        parsed = safe_json_parse(raw_output)

        logger.info(f"[BATCH {batch_id}] ✅ Success for pages {page_nums}")
        return {num: ensure_schema_keys(parsed.get(str(num), {})) for num, _ in batch}

    except Exception as e:
        logger.warning(f"[BATCH {batch_id}] ❌ Failed for pages {page_nums}: {e}")
        return {num: ensure_schema_keys({}) for num, _ in batch}


async def run_pipeline_on_pdf(
    pdf_path: str,
    max_pages: int = 0,        # 0 = all pages
    batch_size: int = 2,
    max_concurrent: int = 3
):
    """
    Async pipeline with parallel Gemini requests.
    max_pages=0 -> process all pages
    """
    logger.info(f"📄 Starting pipeline for {pdf_path}")

    pages = extract_text_with_ocr(pdf_path)
    total_pages = len(pages)

    # Limit to first N pages if set
    limited_pages = pages if max_pages == 0 else dict(list(pages.items())[:max_pages])
    logger.info(f"Processing {len(limited_pages)}/{total_pages} pages")

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY
    )

    schema_text = json.dumps(MASTER_SCHEMA, indent=2)
    page_items = list(limited_pages.items())

    tasks: List[asyncio.Task] = []
    semaphore = asyncio.Semaphore(max_concurrent)  # limit concurrent requests

    async def sem_task(batch, batch_id: int):
        async with semaphore:
            return await process_batch(model, batch, schema_text, batch_id)

    # schedule all batches
    for i in range(0, len(page_items), batch_size):
        batch = page_items[i:i + batch_size]
        batch_id = i // batch_size + 1
        tasks.append(asyncio.create_task(sem_task(batch, batch_id)))

    results = await asyncio.gather(*tasks)

    # merge all results
    page_results: Dict[int, Dict[str, Any]] = {}
    for r in results:
        page_results.update(r)

    merged_schema = merge_schemas(page_results)
    final_schema = ensure_schema_keys(merged_schema)

    logger.info("✅ Pipeline finished successfully")

    return {
        "pages": limited_pages,
        "schema": final_schema,
        "full_text": "\n\n".join(limited_pages.values())
    }
