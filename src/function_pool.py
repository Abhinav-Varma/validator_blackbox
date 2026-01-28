"""
All user-land transformation functions.
Add new helpers here; they will be auto-available in rules.py
"""
from typing import List, Dict, Any
from decimal import Decimal
import json
import pathlib

# ----------  shared data ----------
_GST_MAP_PATH = pathlib.Path(__file__).with_name("gstin_state_codes_india.json")
GST_STATE_CODE_MAP: Dict[str, str] = json.loads(_GST_MAP_PATH.read_text())

# ----------  whitelist of transform steps ----------
def CAPITALIZE(source=None) -> "Step[Any, str]":
    from src.step_engine import Step

    def _cap(v):
        if v is None:
            return None
        s = v if isinstance(v, str) else str(v)
        return s.capitalize()

    # Backwards-compatible: CAPITALIZE() -> Step[str, str]
    # Also supports nested usage: CAPITALIZE(source_step)
    if source is None:
        return Step(_cap)
    if callable(source):
        return Step(lambda blob: _cap(source(blob)))
    return Step(lambda _: _cap(source))

def CONCAT(sep: str = " ") -> "Step[list, str]":
    from src.step_engine import Step
    return Step(lambda pieces: sep.join(map(str, pieces)))

def JOIN() -> "Step[list, str]":
    from src.step_engine import Step
    return Step("".join)

def SPLIT(sep: str = " ") -> "Step[str, tuple[str, ...]]":
    from src.step_engine import Step
    return Step(lambda s: tuple(s.split(sep)))

def join_parts(*parts: Any) -> "Step[Dict[str, Any], str]":
    from src.step_engine import Step
    return Step(lambda blob: "".join(
        (p(blob) if callable(p) else str(p)) for p in parts
    ))

def SUBSTR(start: int, length: int, source=None) -> "Step[Any, str]":
    from src.step_engine import Step

    def _apply_substr(v):
        if v is None:
            return None
        s = v if isinstance(v, str) else str(v)
        return s[start : start + length]

    # Backwards-compatible: SUBSTR(start,length) -> Step[str,str]
    # Also supports nested usage: SUBSTR(start,length, source_step)
    if source is None:
        return Step(_apply_substr)
    if callable(source):
        return Step(lambda blob: _apply_substr(source(blob)))
    return Step(lambda _: _apply_substr(source))

def GST_STATE_NAME() -> "Step[str, str]":
    from src.step_engine import Step
    return Step(
        lambda gst: GST_STATE_CODE_MAP.get(gst[:2], "") if isinstance(gst, str) and len(gst) >= 2 else ""
    )

def GST_DETAILS_ALL() -> "Step[Any, List[Dict[str, str]]]":
    from src.step_engine import Step

    def _impl(records: Any) -> List[Dict[str, str]]:
        # normalise nested list from jsonpath
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
            out.append({"gst_number": gst, "pan_number": pan, "state_name": GST_STATE_CODE_MAP.get(state_code, "")})
        return out

    return Step(_impl)