# app/workflows/pdf_pipeline.py

"""
LangGraph-based Hybrid PDF Pipeline:
 - Step 1: OCR per page (guarantees full text extraction).
 - Step 2: Concatenate all page texts.
 - Step 3: Build prompt & call Gemini once with full document.
 - Step 4: Parse JSON output safely, with auto-fix fallback.
 - Step 5: Ensure schema keys and return result.
"""

import json
import re
from typing import Dict, Any

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from app.utils import extract_text_with_ocr, ensure_schema_keys, MASTER_SCHEMA, GOOGLE_API_KEY


# --- Graph State ---
class PipelineState(dict):
    """
    State object passed between nodes.
    Holds intermediate and final results.
    """
    pages: Dict[int, str]
    full_text: str
    prompt: str
    raw_output: str
    schema: Dict[str, Any]


# --- JSON Parser Node ---
def safe_json_parse(raw_text: str) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Auto-fix prompt if JSON invalid
        fix_prompt = f"""
        The following text is intended to be JSON but is invalid.
        Fix it and return ONLY valid JSON with no extra commentary:
        {raw_text}
        """
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY
        )
        resp = model.invoke([HumanMessage(content=fix_prompt)])
        fixed_text = re.sub(
            r"^```json\s*|\s*```$",
            "",
            getattr(resp, "content", str(resp)).strip(),
            flags=re.MULTILINE
        ).strip()
        return json.loads(fixed_text)


# --- Prompt Builder ---
def build_prompt_for_full_doc(page_texts: Dict[int, str]) -> str:
    schema_text = json.dumps(MASTER_SCHEMA, indent=2)
    pages_text = "\n".join(
        f"--- PAGE {i} ---\n{text}" for i, text in page_texts.items()
    )
    return (
        "You are a strict JSON formatter. "
        "Return ONLY valid JSON with no markdown fences or commentary.\n\n"
        f"Extract information into the following strict JSON schema:\n{schema_text}\n\n"
        f"Document text with page numbers:\n{pages_text}"
    )


# --- Node Functions ---
def node_extract_text(state: PipelineState) -> PipelineState:
    pages = extract_text_with_ocr(state["pdf_path"])
    state["pages"] = pages
    return state


def node_concat_text(state: PipelineState) -> PipelineState:
    full_text = "\n\n".join(
        [f"--- Page {i} ---\n{text}" for i, text in state["pages"].items()]
    )
    state["full_text"] = full_text
    state["prompt"] = build_prompt_for_full_doc(state["pages"])
    return state


def node_call_gemini(state: PipelineState) -> PipelineState:
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
    resp = model.invoke([HumanMessage(content=state["prompt"])])
    state["raw_output"] = getattr(resp, "content", str(resp))
    return state


def node_parse_json(state: PipelineState) -> PipelineState:
    parsed = safe_json_parse(state["raw_output"])
    schema = ensure_schema_keys(parsed)
    state["schema"] = schema
    return state


# --- Build LangGraph ---
graph = StateGraph(PipelineState)

graph.add_node("extract_text", node_extract_text)
graph.add_node("concat_text", node_concat_text)
graph.add_node("call_gemini", node_call_gemini)
graph.add_node("parse_json", node_parse_json)

graph.set_entry_point("extract_text")
graph.add_edge("extract_text", "concat_text")
graph.add_edge("concat_text", "call_gemini")
graph.add_edge("call_gemini", "parse_json")
graph.add_edge("parse_json", END)

compiled_graph = graph.compile()


# --- Runner ---
def run_pipeline_on_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Execute the LangGraph pipeline on a given PDF.
    """
    initial_state = PipelineState(pdf_path=pdf_path)
    final_state = compiled_graph.invoke(initial_state)

    return {
        "pages": final_state["pages"],
        "full_text": final_state["full_text"],
        "schema": final_state["schema"],
    }
