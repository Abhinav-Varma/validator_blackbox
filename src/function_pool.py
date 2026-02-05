"""
All user-land transformation functions.
Add new helpers here; they will be auto-available in rules.py
"""

from typing import List, Dict, Any
import json
import pathlib

from src.step_engine import Step
from src.jsonlogic_engine import jsonLogic

# --------------------------------------------------
# Shared data
# --------------------------------------------------

_GST_MAP_PATH = pathlib.Path(__file__).with_name("gstin_state_codes_india.json")
GST_STATE_CODE_MAP: Dict[str, str] = json.loads(_GST_MAP_PATH.read_text())

# --------------------------------------------------
# String / list transforms (nested-style only)
# --------------------------------------------------

def CAPITALIZE(source) -> "Step[Any, str]":
    def _cap(v):
        return op_capitalize(v)

    return Step(lambda blob: _cap(source(blob)))


def SUBSTR(start: int, length: int, source) -> "Step[Any, str]":
    def _apply_substr(v):
        return op_substr(v, start, length)

    return Step(lambda blob: _apply_substr(source(blob)))


def join_parts(*parts: Any) -> "Step[Dict[str, Any], str]":
    def _join(blob):
        evaluated = [(p(blob) if callable(p) else p) for p in parts]
        return op_join(*evaluated)

    return Step(_join)

# --------------------------------------------------
# JsonLogic-style operator implementations
# --------------------------------------------------

def op_capitalize(v: Any) -> Any:
    if v is None:
        return None
    s = v if isinstance(v, str) else str(v)
    return s.capitalize()


def op_substr(s: Any, start: int, length: int | None = None) -> Any:
    if s is None:
        return None
    ss = s if isinstance(s, str) else str(s)
    if length is None:
        return ss[start:]
    return ss[start:start + length]


def op_join(*parts: Any) -> str:
    return "".join(str(p) for p in parts if p is not None)


# Optional: exposed operator table (JsonLogic-style)

OPERATIONS = {
    "capitalize": op_capitalize,
    "substr": op_substr,
    "cat": op_join,
}

# --------------------------------------------------
# GST helpers
# --------------------------------------------------

def GST_DETAILS_ALL() -> "Step[Any, List[Dict[str, str]]]":
    def _impl(records: Any) -> List[Dict[str, str]]:
        # normalize nested list from jsonpath
        if records and isinstance(records[0], list):
            records = records[0]

        out: list[dict[str, str]] = []

        for rec in records:
            if not isinstance(rec, dict):
                continue

            gst = rec.get("gst_number")
            if not isinstance(gst, str) or len(gst) < 12:
                continue

            state_code = gst[:2]
            pan = gst[2:12]

            out.append({
                "gst_number": gst,
                "pan_number": pan,
                "state_name": GST_STATE_CODE_MAP.get(state_code, "")
            })

        return out

    return Step(_impl)

# --------------------------------------------------
# JsonLogic integration
# --------------------------------------------------

def JSONLOGIC(rule: Dict[str, Any]) -> Step[Dict[str, Any], Any]:
    """
    Execute a JsonLogic rule against the full input blob.
    """
    def _apply(blob: Dict[str, Any]) -> Any:
        return jsonLogic(rule, blob)

    return Step(_apply)
