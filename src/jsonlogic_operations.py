"""
JSONLogic Operations: Operators and expression builders for python-jsonlogic library.
"""
import json, pathlib
from typing import Any
from dataclasses import dataclass, field
from jsonlogic.core import Operator
from jsonlogic.operators import operator_registry
_GST_MAP_PATH = pathlib.Path(__file__).with_name("gstin_state_codes_india.json")
GST_STATE_CODE_MAP: dict = json.loads(_GST_MAP_PATH.read_text())

# Operator classes (registered with python-jsonlogic)
@dataclass
class _JSONPATH(Operator):
    expr: str = field(default="")
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, expr=args[0])
    def evaluate(self, context):
        from jsonpath_ng import parse
        matches = parse(self.expr).find(context.data_stack.tail[0])
        return matches[0].value if len(matches) == 1 else [m.value for m in matches] or None

@dataclass
class _CAPITALIZE(Operator):
    src: Any = field(default=None)
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, src=args[0])
    def evaluate(self, context):
        val = self.src
        if isinstance(val, Operator): val = val.evaluate(context)
        return None if val is None else str(val).capitalize()

@dataclass
class _SUBSTR(Operator):
    start: int = field(default=0)
    length: int = field(default=0)
    src: Any = field(default=None)
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, start=args[0], length=args[1], src=args[2])
    def evaluate(self, context):
        start, length, val = self.start, self.length, self.src
        if isinstance(start, Operator): start = start.evaluate(context)
        if isinstance(length, Operator): length = length.evaluate(context)
        if isinstance(val, Operator): val = val.evaluate(context)
        return None if val is None else str(val)[start:start + length]

@dataclass
class _JOIN_PARTS(Operator):
    parts: list = field(default_factory=list)
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, parts=list(args))
    def evaluate(self, context):
        result = []
        for arg in self.parts:
            val = arg.evaluate(context) if isinstance(arg, Operator) else arg
            result.append("" if val is None else val if isinstance(val, str) else str(val))
        return "".join(result)

@dataclass
class _GST_DETAILS_ALL(Operator):
    src: Any = field(default=None)
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, src=args[0] if args else None)
    def evaluate(self, context):
        records = self.src.evaluate(context) if self.src else context.data_stack.tail[0].get("gst_records", [])
        if not records or not isinstance(records, list): return []
        out = []
        for rec in records:
            if not isinstance(rec, dict): continue
            gst = rec.get("gst_number")
            if isinstance(gst, str) and len(gst) >= 12:
                out.append({"gst_number": gst, "pan_number": gst[2:12], "state_name": GST_STATE_CODE_MAP.get(gst[:2], "")})
        return out

# Register operators
operator_registry.register("JSONPATH", _JSONPATH)
operator_registry.register("CAPITALIZE", _CAPITALIZE)
operator_registry.register("SUBSTR", _SUBSTR)
operator_registry.register("JOIN_PARTS", _JOIN_PARTS)
operator_registry.register("GST_DETAILS_ALL", _GST_DETAILS_ALL)

# Expression builders (for use in rules.py)
def JSONPATH(expr: str) -> dict: return {"JSONPATH": [expr]}
def CAPITALIZE(src: Any) -> dict: return {"CAPITALIZE": [src]}
def SUBSTR(start: int, length: int, src: Any) -> dict: return {"SUBSTR": [start, length, src]}
def JOIN_PARTS(*parts: Any) -> dict: return {"JOIN_PARTS": list(parts)}
def GST_DETAILS_ALL(src: Any = None) -> dict: return {"GST_DETAILS_ALL": []} if src is None else {"GST_DETAILS_ALL": [src]}