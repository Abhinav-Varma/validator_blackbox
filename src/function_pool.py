"""
All user-land transformation functions.
Add new helpers here; they will be auto-available in rules.py
"""

from typing import List, Dict, Any
from decimal import Decimal
import json
import pathlib

<<<<<<< Updated upstream
# ----------  shared data ----------
=======
from src.step_engine import Step
from src.jsonlogic_engine import jsonLogic


# --------------------------------------------------
# Shared data
# --------------------------------------------------

>>>>>>> Stashed changes
_GST_MAP_PATH = pathlib.Path(__file__).with_name("gstin_state_codes_india.json")
GST_STATE_CODE_MAP: Dict[str, str] = json.loads(_GST_MAP_PATH.read_text())

# ----------  helpers ----------
def _resolve_parts(blob: Dict[str, Any], parts: list) -> list[str]:
    """Resolve Path objects inside a list of mixed literals / paths."""
    from src.step_engine import Path
    out: list[str] = []
    for p in parts:
        if isinstance(p, Path):
            out.append(str(p(blob)))
        else:
            out.append(str(p))
    return out

<<<<<<< Updated upstream
# ----------  whitelist of transform steps ----------
def CAPITALIZE() -> "Step[str, str]":
    from src.step_engine import Step
    return Step(str.capitalize)
=======
# --------------------------------------------------
# String / list transforms
# --------------------------------------------------

def CAPITALIZE(source=None) -> "Step[Any, str]":
    # Delegate to jsonlogic-style operator implementation
    def _cap(v):
        return op_capitalize(v)
>>>>>>> Stashed changes

def CONCAT(sep: str = " ") -> "Step[list, str]":
    from src.step_engine import Step
    return Step(lambda pieces: sep.join(map(str, pieces)))

def JOIN() -> "Step[list, str]":
    from src.step_engine import Step
    return Step("".join)

<<<<<<< Updated upstream
def SPLIT(sep: str = " ") -> "Step[str, tuple[str, ...]]":
    from src.step_engine import Step
    return Step(lambda s: tuple(s.split(sep)))

def join_parts(*parts: Any) -> "Step[Dict[str, Any], str]":
    from src.step_engine import Step
    return Step(lambda blob: "".join(
        (p(blob) if callable(p) else str(p)) for p in parts
    ))

def SUBSTR(start: int, length: int) -> "Step[str, str]":
    from src.step_engine import Step
    return Step(lambda s: s[start : start + length])

def GST_STATE_NAME() -> "Step[str, str]":
    from src.step_engine import Step
    return Step(
        lambda gst: GST_STATE_CODE_MAP.get(gst[:2], "") if isinstance(gst, str) and len(gst) >= 2 else ""
    )
=======
def SUBSTR(start: int, length: int, source=None) -> "Step[Any, str]":
    def _apply_substr(v):
        return op_substr(v, start, length)

    if source is None:
        return Step(_apply_substr)
    if callable(source):
        return Step(lambda blob: _apply_substr(source(blob)))
    return Step(lambda _: _apply_substr(source))


def join_parts(*parts: Any) -> "Step[Dict[str, Any], str]":
    def _join(blob):
        evaluated = [(p(blob) if callable(p) else p) for p in parts]
        return op_join(*evaluated)

    return Step(_join)


# ------------------------------------------------------------------
# JsonLogic-style operator implementations (plain functions)
# These mirror the style used in jsonlogic's `operations` dict and
# are exposed so other code can call them directly if desired.
# ------------------------------------------------------------------


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


# Expose an OPERATIONS-like dict similar to jsonlogic
OPERATIONS = {
    "capitalize": op_capitalize,
    "substr": op_substr,
    "cat": op_join,
}


# --------------------------------------------------
# GST helpers
# --------------------------------------------------
>>>>>>> Stashed changes

def GST_DETAILS_ALL() -> "Step[Any, List[Dict[str, str]]]":
    from src.step_engine import Step

    def _impl(records: Any) -> List[Dict[str, str]]:
<<<<<<< Updated upstream
        # normalise nested list from jsonpath
=======
        # normalize nested list from jsonpath
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    return Step(_impl)
=======
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
>>>>>>> Stashed changes
