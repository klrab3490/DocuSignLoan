import re
import uuid
import json
import fitz
from pydantic import BaseModel
from typing import Dict, Any, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.utils import (
    client,
    delete_temp_file,
    load_jobs_from_file,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    save_file_permanent,
    save_jobs_to_file,
)

router = APIRouter()
processing_jobs = load_jobs_from_file()

# -------------------------------
# Pydantic Models for Validation
# -------------------------------

class AvailabilityPeriod(BaseModel):
    start: Optional[str]
    end: Optional[str]

class Dates(BaseModel):
    agreement_date: Optional[str]
    effective_date: Optional[str]
    maturity_date: Optional[str]
    end_date_respective_facility: Optional[str]
    availability_periods: Optional[Dict[str, AvailabilityPeriod]]

class General(BaseModel):
    borrower: Optional[str]
    agent: Optional[str]
    security_agent: Optional[str]
    sponsor_name: Optional[str]
    majority_lenders: Optional[str]

class Definitions(BaseModel):
    lma_defined_term: Optional[str]
    reference_bank_definition: Optional[str]
    base_currency: Optional[str]
    optional_currencies: Optional[str]
    disqualified_lender_definition: Optional[str]

class CreditFacilities(BaseModel):
    facility_name: Optional[str]
    facility_type: Optional[str]
    facility_size: Optional[str]
    revolver_size: Optional[str]
    total_facility_size: Optional[str]
    sub_limit_commitments: Optional[str]
    loan_commitments: Optional[Dict[str, str]]
    repayment_provisions: Optional[Dict[str, str]]
    facility_extension_options: Optional[Dict[str, str]]
    interest_and_margin: Optional[Dict[str, str]]

class Covenants(BaseModel):
    interest_coverage_text: Optional[str]
    interest_coverage_tables: Optional[str]
    fixed_charge_coverage_text: Optional[str]
    fixed_charge_coverage_tables: Optional[str]
    total_leverage_text: Optional[str]
    total_leverage_tables: Optional[str]
    restricted_asset_sales: Optional[str]
    permitted_transfers: Optional[str]
    permitted_acquisitions: Optional[str]
    indebtedness_clauses: Optional[str]
    prepayment_from_asset_sales: Optional[str]
    reinvestment_period: Optional[str]
    equity_cure_provision: Optional[str]
    subsidiary_guarantees: Optional[str]
    transfer_provisions: Optional[str]
    amendment_clause: Optional[str]
    snooze_lose_clause: Optional[str]
    disqualified_lender_list: Optional[str]

class RepresentationsAndWarranties(BaseModel):
    use_of_proceeds: Optional[str]
    facility_proceeds: Optional[str]
    material_adverse_change: Optional[str]

class Defaults(BaseModel):
    events_of_default: Optional[str]
    payment_default: Optional[str]
    insolvency_default: Optional[str]
    misrepresentation_default: Optional[str]
    market_disruption_clause: Optional[str]
    cross_default: Optional[str]
    cross_acceleration: Optional[str]
    set_off: Optional[str]
    set_off_prohibited_for_borrower: Optional[str]

class Miscellaneous(BaseModel):
    bilateral_or_syndicated: Optional[str]
    business_day_convention: Optional[str]
    business_day_payments: Optional[str]
    business_day_rate_setting: Optional[str]
    governing_law: Optional[str]
    confidentiality_clause: Optional[str]
    client_communication_language: Optional[str]

class ExtractedData(BaseModel):
    dates: Optional[Dates]
    general: Optional[General]
    definitions: Optional[Definitions]
    credit_facilities: Optional[CreditFacilities]
    covenants: Optional[Covenants]
    representations_and_warranties: Optional[RepresentationsAndWarranties]
    defaults: Optional[Defaults]
    miscellaneous: Optional[Miscellaneous]

class PageExtraction(BaseModel):
    page_number: int
    extracted_data: ExtractedData

class ExtractResponse(BaseModel):
    job_id: str
    text_content: str  # raw JSON string
    pages: Dict[int, str]  # page_number → raw text


# -------------------------------
# Helpers
# -------------------------------

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


# -------------------------------
# Endpoint
# -------------------------------

@router.post("/extract-and-format/", response_model=ExtractResponse)
async def extract_and_format_pdf(
    file: UploadFile = File(...),
    format_instructions: str = (
    "Extract information into the following strict JSON schema. "
    "For each category, return its fields as key-value pairs. "
    "Each field must be represented as an object with: "
    "{ 'value': str, 'page_number': int }. "
    "Schema:\n"
    "{ "
    "'dates': {"
    "  'agreement_date': { 'value': str, 'page_number': int }, "
    "  'effective_date': { 'value': str, 'page_number': int }, "
    "  'maturity_date': { 'value': str, 'page_number': int }, "
    "  'end_date_of_respective_facility': { 'value': str, 'page_number': int }, "
    "  'start_date_of_facility_availability_period_facility_a': { 'value': str, 'page_number': int }, "
    "  'end_date_of_facility_availability_period_facility_a': { 'value': str, 'page_number': int }, "
    "  'start_date_of_facility_availability_period_facility_b': { 'value': str, 'page_number': int }, "
    "  'end_date_of_facility_availability_period_facility_b': { 'value': str, 'page_number': int } "
    "}, "
    "'general': {"
    "  'borrower': { 'value': str, 'page_number': int }, "
    "  'agent': { 'value': str, 'page_number': int }, "
    "  'security_agent': { 'value': str, 'page_number': int }, "
    "  'sponsor_name': { 'value': str, 'page_number': int }, "
    "  'majority_lenders': { 'value': str, 'page_number': int } "
    "}, "
    "'definitions': {"
    "  'lma_defined_term': { 'value': str, 'page_number': int }, "
    "  'reference_bank_definition': { 'value': str, 'page_number': int }, "
    "  'base_currency': { 'value': str, 'page_number': int }, "
    "  'optional_currencies': { 'value': str, 'page_number': int }, "
    "  'disqualified_lender_definition': { 'value': str, 'page_number': int } "
    "}, "
    "'credit_facilities': {"
    "  'stated_term_of_facility': { 'value': str, 'page_number': int }, "
    "  'facility_name': { 'value': str, 'page_number': int }, "
    "  'facility_type': { 'value': str, 'page_number': int }, "
    "  'facility_size_term': { 'value': str, 'page_number': int }, "
    "  'facility_size_revolver': { 'value': str, 'page_number': int }, "
    "  'total_facility_size': { 'value': str, 'page_number': int }, "
    "  'total_commitments': { 'value': str, 'page_number': int }, "
    "  'loan_commitments': { 'value': str, 'page_number': int }, "
    "  'term_loan_commitments': { 'value': str, 'page_number': int }, "
    "  'revolving_loan_commitments': { 'value': str, 'page_number': int }, "
    "  'repayment_provision': { 'value': str, 'page_number': int }, "
    "  'repayment_type': { 'value': str, 'page_number': int }, "
    "  'mandatory_repayment': { 'value': str, 'page_number': int }, "
    "  'mandatory_prepayment_due_to_change_of_control': { 'value': str, 'page_number': int }, "
    "  'voluntary_prepayment': { 'value': str, 'page_number': int }, "
    "  'call_protection_prepayment_clause': { 'value': str, 'page_number': int }, "
    "  'facility_extension_options': { 'value': str, 'page_number': int }, "
    "  'facility_extension_option_how_many_years': { 'value': str, 'page_number': int }, "
    "  'amend_to_extend_clause': { 'value': str, 'page_number': int }, "
    "  'number_of_extension_options': { 'value': str, 'page_number': int }, "
    "  'lender_discretion': { 'value': str, 'page_number': int }, "
    "  'calculation_of_interest': { 'value': str, 'page_number': int }, "
    "  'initial_margin_text': { 'value': str, 'page_number': int }, "
    "  'initial_margin_tables': { 'value': str, 'page_number': int }, "
    "  'interest_rate_convention': { 'value': str, 'page_number': int }, "
    "  'interest_rate_floor': { 'value': str, 'page_number': int }, "
    "  'libor_definition': { 'value': str, 'page_number': int }, "
    "  'arrangement_fees': { 'value': str, 'page_number': int }, "
    "  'agency_fees': { 'value': str, 'page_number': int } "
    "}, "
    "'representations_and_warranties': {"
    "  'use_of_proceeds': { 'value': str, 'page_number': int }, "
    "  'material_adverse_change_clause': { 'value': str, 'page_number': int } "
    "}, "
    "'covenants': {"
    "  'interest_coverage_covenant': { 'value': str, 'page_number': int }, "
    "  'interest_coverage_text': { 'value': str, 'page_number': int }, "
    "  'interest_coverage_tables': { 'value': str, 'page_number': int }, "
    "  'total_leverage_covenant': { 'value': str, 'page_number': int }, "
    "  'total_leverage_text': { 'value': str, 'page_number': int }, "
    "  'total_leverage_tables': { 'value': str, 'page_number': int }, "
    "  'restricted_asset_sales_permitted_transfers': { 'value': str, 'page_number': int }, "
    "  'permitted_acquisitions_clause_text': { 'value': str, 'page_number': int }, "
    "  'permitted_indebtedness_basket': { 'value': str, 'page_number': int }, "
    "  'permitted_financial_indebtedness_text': { 'value': str, 'page_number': int }, "
    "  'prepayment_from_asset_sales_proceeds_clause': { 'value': str, 'page_number': int }, "
    "  'percent_of_net_cash_proceeds': { 'value': str, 'page_number': int }, "
    "  'permitted_reinvestment_period': { 'value': str, 'page_number': int }, "
    "  'equity_cure_provision': { 'value': str, 'page_number': int }, "
    "  'number_of_equity_cures': { 'value': str, 'page_number': int }, "
    "  'subsidiary_guarantees': { 'value': str, 'page_number': int }, "
    "  'transfer_provisions': { 'value': str, 'page_number': int }, "
    "  'amendment_clause': { 'value': str, 'page_number': int }, "
    "  'snooze_lose_clause': { 'value': str, 'page_number': int }, "
    "  'disqualified_lender_list': { 'value': str, 'page_number': int } "
    "}, "
    "'defaults': {"
    "  'events_of_default': { 'value': str, 'page_number': int }, "
    "  'payment_default_provision': { 'value': str, 'page_number': int }, "
    "  'insolvency_default': { 'value': str, 'page_number': int }, "
    "  'misrepresentation_default': { 'value': str, 'page_number': int }, "
    "  'market_disruption_clause': { 'value': str, 'page_number': int }, "
    "  'cross_default': { 'value': str, 'page_number': int }, "
    "  'cross_acceleration': { 'value': str, 'page_number': int }, "
    "  'no_set_off': { 'value': str, 'page_number': int }, "
    "  'set_off_prohibited_for_borrower': { 'value': str, 'page_number': int } "
    "}, "
    "'miscellaneous': {"
    "  'bilateral_or_syndicated': { 'value': str, 'page_number': int }, "
    "  'business_days_convention_calendar': { 'value': str, 'page_number': int }, "
    "  'business_days_payments_non_business_day_rule': { 'value': str, 'page_number': int }, "
    "  'business_days_rate_setting_quotation_day': { 'value': str, 'page_number': int }, "
    "  'governing_law': { 'value': str, 'page_number': int }, "
    "  'confidentiality_clause': { 'value': str, 'page_number': int }, "
    "  'language_for_client_communication': { 'value': str, 'page_number': int } "
    "} "
    "}"
)

):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    # Save uploaded file temporarily in uploads/temp/
    [file_path, temp_file_path] = await save_file_permanent(file)

    # Reopen the saved file for PyMuPDF
    with open(temp_file_path, "rb") as f:
        pdf_bytes = f.read()

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
        processing_jobs[job_id]["file_path"] = file_path
        save_jobs_to_file(processing_jobs)
        await delete_temp_file(file)

        return ExtractResponse(
            job_id=job_id,
            text_content=json.dumps(parsed_json, ensure_ascii=False),
            pages=page_texts
        )

    except Exception as e:
        await delete_temp_file(file)
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = str(e)
        save_jobs_to_file(processing_jobs)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
