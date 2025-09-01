# app/utils/schema.py
"""
Master schema definition and helpers to normalize/ensure keys.

Each final field value should be an object:
    { "value": <str or None>, "page_number": <int or None> }
"""

from typing import Dict, Any

MASTER_SCHEMA = {
    "dates": {
        "agreement_date": None,
        "effective_date": None,
        "maturity_date": None,
        "end_date_of_respective_facility": None,
        "start_date_of_facility_availability_period_facility_a": None,
        "end_date_of_facility_availability_period_facility_a": None,
        "start_date_of_facility_availability_period_facility_b": None,
        "end_date_of_facility_availability_period_facility_b": None,
    },
    "general": {
        "borrower": None,
        "agent": None,
        "security_agent": None,
        "sponsor_name": None,
        "majority_lenders": None,
    },
    "definitions": {
        "lma_defined_term": None,
        "reference_bank_definition": None,
        "base_currency": None,
        "optional_currencies": None,
        "disqualified_lender_definition": None,
    },
    "credit_facilities": {
        "stated_term_of_facility": None,
        "facility_name": None,
        "facility_type": None,
        "facility_size_term": None,
        "facility_size_revolver": None,
        "total_facility_size": None,
        "total_commitments": None,
        "loan_commitments": None,
        "term_loan_commitments": None,
        "revolving_loan_commitments": None,
        "repayment_provision": None,
        "repayment_type": None,
        "mandatory_repayment": None,
        "mandatory_prepayment_due_to_change_of_control": None,
        "voluntary_prepayment": None,
        "call_protection_prepayment_clause": None,
        "facility_extension_options": None,
        "facility_extension_option_how_many_years": None,
        "amend_to_extend_clause": None,
        "number_of_extension_options": None,
        "lender_discretion": None,
        "calculation_of_interest": None,
        "initial_margin_text": None,
        "initial_margin_tables": None,
        "interest_rate_convention": None,
        "interest_rate_floor": None,
        "libor_definition": None,
        "arrangement_fees": None,
        "agency_fees": None,
    },
    "representations_and_warranties": {
        "use_of_proceeds": None,
        "material_adverse_change_clause": None,
    },
    "covenants": {
        "interest_coverage_covenant": None,
        "interest_coverage_text": None,
        "interest_coverage_tables": None,
        "total_leverage_covenant": None,
        "total_leverage_text": None,
        "total_leverage_tables": None,
        "restricted_asset_sales_permitted_transfers": None,
        "permitted_acquisitions_clause_text": None,
        "permitted_indebtedness_basket": None,
        "permitted_financial_indebtedness_text": None,
        "prepayment_from_asset_sales_proceeds_clause": None,
        "percent_of_net_cash_proceeds": None,
        "permitted_reinvestment_period": None,
        "equity_cure_provision": None,
        "number_of_equity_cures": None,
        "subsidiary_guarantees": None,
        "transfer_provisions": None,
        "amendment_clause": None,
        "snooze_lose_clause": None,
        "disqualified_lender_list": None,
    },
    "defaults": {
        "events_of_default": None,
        "payment_default_provision": None,
        "insolvency_default": None,
        "misrepresentation_default": None,
        "market_disruption_clause": None,
        "cross_default": None,
        "cross_acceleration": None,
        "no_set_off": None,
        "set_off_prohibited_for_borrower": None,
    },
    "miscellaneous": {
        "bilateral_or_syndicated": None,
        "business_days_convention_calendar": None,
        "business_days_payments_non_business_day_rule": None,
        "business_days_rate_setting_quotation_day": None,
        "governing_law": None,
        "confidentiality_clause": None,
        "language_for_client_communication": None,
    },
}


def ensure_schema_keys(struct: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Ensure that a structure has all sections/fields from MASTER_SCHEMA.
    For each field, return an object of shape: { "value": <...>, "page_number": <...> }.
    If the incoming struct provides a raw value or a dict, normalize it.

    Example inputs accepted for a field:
      - None
      - "some text"
      - {"value": "some text", "page_number": 3}

    Output guarantees:
      - All MASTER_SCHEMA sections and fields are present.
      - Each field is an object {"value": <str|None>, "page_number": <int|None>}
    """
    def normalize_field(val):
        if isinstance(val, dict):
            # respect keys if present
            return {"value": val.get("value"), "page_number": val.get("page_number")}
        if val is None:
            return {"value": None, "page_number": None}
        # scalar value -> assume found on unknown page (leave page_number None)
        return {"value": val, "page_number": None}

    out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for section, fields in MASTER_SCHEMA.items():
        out[section] = {}
        incoming_section = struct.get(section, {}) if isinstance(struct, dict) else {}
        for key in fields.keys():
            if key in incoming_section:
                out[section][key] = normalize_field(incoming_section[key])
            else:
                out[section][key] = {"value": None, "page_number": None}
    return out
