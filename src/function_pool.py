"""
All user-land transformation functions.
"""
from typing import List, Dict, Any
import json
import pathlib

from src.step_engine import Step


_GST_MAP_PATH = pathlib.Path(__file__).with_name("gstin_state_codes_india.json")
GST_STATE_CODE_MAP: Dict[str, str] = json.loads(_GST_MAP_PATH.read_text())


def CAPITALIZE(source=None) -> "Step[Any, str]":
    def _cap(v):
        if v is None:
            return None
        s = v if isinstance(v, str) else str(v)
        return s.capitalize()

    if source is None:
        return Step(_cap)
    if callable(source):
        return Step(lambda blob: _cap(source(blob)))
    return Step(lambda _: _cap(source))


def SUBSTR(start: int, length: int, source=None) -> "Step[Any, str]":
    def _apply_substr(v):
        if v is None:
            return None
        s = v if isinstance(v, str) else str(v)
        return s[start : start + length]

    if source is None:
        return Step(_apply_substr)
    if callable(source):
        return Step(lambda blob: _apply_substr(source(blob)))
    return Step(lambda _: _apply_substr(source))


def join_parts(*parts: Any) -> "Step[Dict[str, Any], str]":
    return Step(lambda blob: "".join(
        (p(blob) if callable(p) else str(p)) for p in parts
    ))


def GST_DETAILS_ALL() -> "Step[Any, List[Dict[str, str]]]":
    def _impl(records: Any) -> List[Dict[str, str]]:
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
