# app/utils/merge_utils.py
from typing import Dict, List, Any
from .schema import MASTER_SCHEMA, ensure_schema_keys


def _take_first_non_null(a: Dict[str, Any] | None, b: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Merge two field objects {value, page_number}, preferring the first
    non-null 'value'. If both are empty, return a null placeholder.
    """
    default = {"value": None, "page_number": None}

    if not a and not b:
        return default

    if a and a.get("value") not in (None, ""):
        return a

    if b and b.get("value") not in (None, ""):
        return b

    return default


def merge_page_structs_into_master(page_structs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Merge multiple per-page structured dicts into a single MASTER_SCHEMA-shaped dict.
    
    - Keeps the first non-null occurrence across pages for each field.
    - Ensures all schema keys exist (using ensure_schema_keys).
    """
    # Initialize with a skeleton schema
    merged = ensure_schema_keys({})

    for struct in page_structs or []:
        normalized = ensure_schema_keys(struct)
        for section, fields in normalized.items():
            for key, obj in fields.items():
                merged[section][key] = _take_first_non_null(
                    merged[section].get(key), obj
                )

    return merged
