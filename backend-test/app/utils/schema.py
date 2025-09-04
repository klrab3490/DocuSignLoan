# app/utils/schema.py
"""
Master schema definition and helpers to normalize/ensure keys.

Each final field value is always an object of shape:
    { "value": <str or None>, "page_number": <int or None> }

Functions:
- get_empty_schema(): returns a deep copy of MASTER_SCHEMA
- ensure_schema_keys(): normalizes an incoming structure to match MASTER_SCHEMA
"""

from typing import Dict, Any, Optional
import copy

# ---------------- Master Schema ---------------- #
MASTER_SCHEMA: Dict[str, Dict[str, Dict[str, Optional[Any]]]] = {
    "dates": {
        "agreement_date": {"value": None, "page_number": None},
        "effective_date": {"value": None, "page_number": None},
        "maturity_date": {"value": None, "page_number": None},
        "end_date_of_respective_facility": {"value": None, "page_number": None},
        "start_date_of_facility_availability_period_facility_a": {"value": None, "page_number": None},
        "end_date_of_facility_availability_period_facility_a": {"value": None, "page_number": None},
        "start_date_of_facility_availability_period_facility_b": {"value": None, "page_number": None},
        "end_date_of_facility_availability_period_facility_b": {"value": None, "page_number": None},
    },
    "general": {
        "borrower": {"value": None, "page_number": None},
        "agent": {"value": None, "page_number": None},
        "security_agent": {"value": None, "page_number": None},
        "sponsor_name": {"value": None, "page_number": None},
        "majority_lenders": {"value": None, "page_number": None},
    },
    "definitions": {
        "lma_defined_term": {"value": None, "page_number": None},
        "reference_bank_definition": {"value": None, "page_number": None},
        "base_currency": {"value": None, "page_number": None},
        "optional_currencies": {"value": None, "page_number": None},
        "disqualified_lender_definition": {"value": None, "page_number": None},
    },
    "credit_facilities": {
        "stated_term_of_facility": {"value": None, "page_number": None},
        "facility_name": {"value": None, "page_number": None},
        "facility_type": {"value": None, "page_number": None},
        "facility_size_term": {"value": None, "page_number": None},
        "facility_size_revolver": {"value": None, "page_number": None},
        "total_facility_size": {"value": None, "page_number": None},
        "total_commitments": {"value": None, "page_number": None},
        "loan_commitments": {"value": None, "page_number": None},
        "term_loan_commitments": {"value": None, "page_number": None},
        "revolving_loan_commitments": {"value": None, "page_number": None},
        "repayment_provision": {"value": None, "page_number": None},
        "repayment_type": {"value": None, "page_number": None},
        "mandatory_repayment": {"value": None, "page_number": None},
        "mandatory_prepayment_due_to_change_of_control": {"value": None, "page_number": None},
        "voluntary_prepayment": {"value": None, "page_number": None},
        "call_protection_prepayment_clause": {"value": None, "page_number": None},
        "facility_extension_options": {"value": None, "page_number": None},
        "facility_extension_option_how_many_years": {"value": None, "page_number": None},
        "amend_to_extend_clause": {"value": None, "page_number": None},
        "number_of_extension_options": {"value": None, "page_number": None},
        "lender_discretion": {"value": None, "page_number": None},
        "calculation_of_interest": {"value": None, "page_number": None},
        "initial_margin_text": {"value": None, "page_number": None},
        "initial_margin_tables": {"value": None, "page_number": None},
        "interest_rate_convention": {"value": None, "page_number": None},
        "interest_rate_floor": {"value": None, "page_number": None},
        "libor_definition": {"value": None, "page_number": None},
        "arrangement_fees": {"value": None, "page_number": None},
        "agency_fees": {"value": None, "page_number": None},
    },
    "representations_and_warranties": {
        "use_of_proceeds": {"value": None, "page_number": None},
        "material_adverse_change_clause": {"value": None, "page_number": None},
    },
    "covenants": {
        "interest_coverage_covenant": {"value": None, "page_number": None},
        "interest_coverage_text": {"value": None, "page_number": None},
        "interest_coverage_tables": {"value": None, "page_number": None},
        "total_leverage_covenant": {"value": None, "page_number": None},
        "total_leverage_text": {"value": None, "page_number": None},
        "total_leverage_tables": {"value": None, "page_number": None},
        "restricted_asset_sales_permitted_transfers": {"value": None, "page_number": None},
        "permitted_acquisitions_clause_text": {"value": None, "page_number": None},
        "permitted_indebtedness_basket": {"value": None, "page_number": None},
        "permitted_financial_indebtedness_text": {"value": None, "page_number": None},
        "prepayment_from_asset_sales_proceeds_clause": {"value": None, "page_number": None},
        "percent_of_net_cash_proceeds": {"value": None, "page_number": None},
        "permitted_reinvestment_period": {"value": None, "page_number": None},
        "equity_cure_provision": {"value": None, "page_number": None},
        "number_of_equity_cures": {"value": None, "page_number": None},
        "subsidiary_guarantees": {"value": None, "page_number": None},
        "transfer_provisions": {"value": None, "page_number": None},
        "amendment_clause": {"value": None, "page_number": None},
        "snooze_lose_clause": {"value": None, "page_number": None},
        "disqualified_lender_list": {"value": None, "page_number": None},
    },
    "defaults": {
        "events_of_default": {"value": None, "page_number": None},
        "payment_default_provision": {"value": None, "page_number": None},
        "insolvency_default": {"value": None, "page_number": None},
        "misrepresentation_default": {"value": None, "page_number": None},
        "market_disruption_clause": {"value": None, "page_number": None},
        "cross_default": {"value": None, "page_number": None},
        "cross_acceleration": {"value": None, "page_number": None},
        "no_set_off": {"value": None, "page_number": None},
        "set_off_prohibited_for_borrower": {"value": None, "page_number": None},
    },
    "miscellaneous": {
        "bilateral_or_syndicated": {"value": None, "page_number": None},
        "business_days_convention_calendar": {"value": None, "page_number": None},
        "business_days_payments_non_business_day_rule": {"value": None, "page_number": None},
        "business_days_rate_setting_quotation_day": {"value": None, "page_number": None},
        "governing_law": {"value": None, "page_number": None},
        "confidentiality_clause": {"value": None, "page_number": None},
        "language_for_client_communication": {"value": None, "page_number": None},
    },
}


# ---------------- Helper Functions ---------------- #

def get_empty_schema() -> Dict[str, Dict[str, Dict[str, Optional[Any]]]]:
    """Return a deep copy of the empty schema so it can be safely mutated."""
    return copy.deepcopy(MASTER_SCHEMA)


def ensure_schema_keys(
    struct: dict[str, dict[str, Any] | Any] | None
) -> dict[str, dict[str, dict[str, Optional[Any]]]]:
    """
    Ensure that a structure has all sections/fields from MASTER_SCHEMA.
    For each field, return an object of shape: { "value": <...>, "page_number": <...> }.
    If the incoming struct provides a raw value or a dict, normalize it.
    """

    def normalize_field(val: Any) -> dict[str, Optional[Any]]:
        if isinstance(val, dict):
            return {"value": val.get("value"), "page_number": val.get("page_number")}
        if val is None:
            return {"value": None, "page_number": None}
        # Coerce numbers and lists to string
        if isinstance(val, (int, float, list)):
            val = str(val)
        return {"value": val, "page_number": None}

    out = get_empty_schema()

    if not isinstance(struct, dict):
        return out

    for section, fields in out.items():
        incoming_section = struct.get(section, {})
        if not isinstance(incoming_section, dict):
            continue
        for key in fields.keys():
            if key in incoming_section:
                out[section][key] = normalize_field(incoming_section[key])

    return out
