# app/utils/merge_utils.py
from copy import deepcopy
from typing import Dict, List, Any

from .schema import MASTER_SCHEMA, ensure_schema_keys


def _take_first_non_null(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two field objects {value, page_number} preferring the first non-null (a),
    otherwise return b, otherwise an empty {value: None, page_number: None}.
    """
    if not a:
        return b if b else {"value": None, "page_number": None}
    a_val = a.get("value")
    if a_val is not None and a_val != "":
        return a
    if b and b.get("value") not in (None, ""):
        return b
    return {"value": None, "page_number": None}


def merge_page_structs_into_master(page_structs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    page_structs: list of per-page structured dicts (each should be a mapping
                  matching MASTER_SCHEMA partially or fully)
    Returns a single MASTER_SCHEMA-shaped dict where for each field we keep the
    first non-null occurrence across pages.
    """
    # start with skeleton (all keys present, values = {"value": None, "page_number": None})
    merged = ensure_schema_keys({})

    for struct in page_structs:
        normalized = ensure_schema_keys(struct)
        for section, fields in normalized.items():
            for key, obj in fields.items():
                merged[section][key] = _take_first_non_null(merged[section].get(key), obj)

    return merged
