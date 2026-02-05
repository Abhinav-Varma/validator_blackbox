"""
All user-land transformation functions.
"""
from typing import Any, List, Optional
import json
import pathlib
from jsonpath_ng import parse

# Import expression builders/types. This import is safe because
# `function_pool` provides pure functions and the import doesn't
# trigger execution that depends on `function_pool` itself.
from src.custom_types import PathExpr, OpExpr


def path(jsonpath: str) -> PathExpr:
    return PathExpr(jsonpath)


def CAPITALIZE(source) -> OpExpr:
    return OpExpr("capitalize", [source])


def SUBSTR(source, start, length) -> OpExpr:
    return OpExpr("substr", [source, start, length])


def join_parts(*parts: Any) -> OpExpr:
    return OpExpr("join_parts", list(parts))


def GST_DETAILS_ALL(source) -> OpExpr:
    return OpExpr("gst_details_all", [source])


# --- Operation implementations (shared) ---

_GST_MAP_PATH = pathlib.Path(__file__).parent / "gstin_state_codes_india.json"
_GST_STATE_CODE_MAP = None


def get_gst_state_code_map():
    """Lazy-load and cache the GST state code map.

    This avoids module-level file I/O during import which makes testing
    and mocking easier and prevents failures when the file is missing
    at import time.
    """
    global _GST_STATE_CODE_MAP
    if _GST_STATE_CODE_MAP is None:
        try:
            _GST_STATE_CODE_MAP = json.loads(_GST_MAP_PATH.read_text())
        except Exception:
            # If file missing or unreadable, fall back to an empty map
            _GST_STATE_CODE_MAP = {}
    return _GST_STATE_CODE_MAP


def op_capitalize(args: List[Any], data: Optional[Any] = None):
    v = args[0] if args else None
    if v is None:
        return None
    return str(v).capitalize()


def op_substr(args: List[Any], data: Optional[Any] = None):
    v = args[0] if len(args) > 0 else None
    start = args[1] if len(args) > 1 else 0
    length = args[2] if len(args) > 2 else 0
    if v is None:
        return None
    s = str(v)
    return s[start:start + length]


def op_join_parts(args: List[Any], data: Optional[Any] = None):
    return "".join(str(a) for a in args)


def op_gst_details_all(args: List[Any], data: Optional[Any] = None):
    records = args[0] if args else None
    if records and isinstance(records, list) and len(records) > 0 and isinstance(records[0], list):
        records = records[0]
    out = []
    for rec in records if records else []:
        if not isinstance(rec, dict):
            continue
        gst = rec.get("gst_number")
        if not isinstance(gst, str) or len(gst) < 12:
            continue
        state_code = gst[:2]
        pan = gst[2:12]
        gst_map = get_gst_state_code_map()
        out.append({
            "gst_number": gst,
            "pan_number": pan,
            "state_name": gst_map.get(state_code, "")
        })
    return out


def op_path(args: List[Any], data: Optional[Any] = None):
    jsonpath = args[0] if args else "$"
    target = args[1] if len(args) > 1 else (data if data is not None else {})
    compiled = parse(jsonpath)
    matches = compiled.find(target)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].value
    return [m.value for m in matches]


_DISPATCH = {
    "capitalize": op_capitalize,
    "substr": op_substr,
    "join_parts": op_join_parts,
    "gst_details_all": op_gst_details_all,
    "path": op_path,
}


def execute(op: str, args: List[Any], data: Optional[Any] = None):
    fn = _DISPATCH.get(op)
    if fn is None:
        raise ValueError(f"Unknown operation: {op}")
    return fn(args, data=data)


KNOWN_OPERATORS = set(_DISPATCH.keys())
