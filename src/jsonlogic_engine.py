"""
JSONLogic compiler and execution engine.
"""
import json
import pathlib
from typing import Any, Dict, List, Union

from jsonpath_ng import parse

from src.custom_types import PathExpr, OpExpr


# Load GST state codes
_GST_MAP_PATH = pathlib.Path(__file__).parent / "gstin_state_codes_india.json"
GST_STATE_CODE_MAP = json.loads(_GST_MAP_PATH.read_text())

# Known JSONLogic operators
KNOWN_OPERATORS = {
    "capitalize", "substr", "join_parts", "gst_details_all", "path",
    # Standard JSONLogic operators could be added here
}


def jsonlogic_apply(logic: Any, data: Any) -> Any:
    """
    Execute JSONLogic against the provided data.
    
    For simple literals (int, str, bool, None), return as-is.
    For JSONLogic dict like {"+": [1, 2]}, recursively evaluate and apply the operation.
    """
    # Handle simple literals
    if logic is None or isinstance(logic, (int, float, str, bool)):
        return logic
    
    # Handle lists - recursively apply to each element
    if isinstance(logic, list):
        return [jsonlogic_apply(item, data) for item in logic]
    
    # Handle dicts
    if isinstance(logic, dict):
        # If empty dict, return as-is
        if not logic:
            return logic
        
        # Check if this is a JSONLogic operation (single key that is a known operator)
        if len(logic) == 1:
            op = next(iter(logic.keys()))
            if op in KNOWN_OPERATORS:
                args = logic[op]
                
                # Recursively evaluate arguments
                if isinstance(args, list):
                    evaluated_args = [jsonlogic_apply(arg, data) for arg in args]
                else:
                    evaluated_args = [jsonlogic_apply(args, data)]
                
                # Apply custom operators
                if op == "capitalize":
                    v = evaluated_args[0] if evaluated_args else None
                    if v is None:
                        return None
                    s = v if isinstance(v, str) else str(v)
                    return s.capitalize()
                
                elif op == "substr":
                    v = evaluated_args[0] if len(evaluated_args) > 0 else None
                    start = evaluated_args[1] if len(evaluated_args) > 1 else 0
                    length = evaluated_args[2] if len(evaluated_args) > 2 else 0
                    if v is None:
                        return None
                    s = v if isinstance(v, str) else str(v)
                    return s[start:start + length]
                
                elif op == "join_parts":
                    return "".join(str(arg) for arg in evaluated_args)
                
                elif op == "gst_details_all":
                    records = evaluated_args[0] if evaluated_args else None
                    
                    # Handle nested list case
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
                        out.append({
                            "gst_number": gst,
                            "pan_number": pan,
                            "state_name": GST_STATE_CODE_MAP.get(state_code, "")
                        })
                    return out
                
                elif op == "path":
                    # Path operation - resolve JSONPath
                    jsonpath = evaluated_args[0] if evaluated_args else "$"
                    target_data = evaluated_args[1] if len(evaluated_args) > 1 else data
                    compiled = parse(jsonpath)
                    matches = compiled.find(target_data)
                    if not matches:
                        return None
                    if len(matches) == 1:
                        return matches[0].value
                    return [m.value for m in matches]
        
        # Not a known operation - treat as regular dict (but still apply recursively to values)
        return {k: jsonlogic_apply(v, data) for k, v in logic.items()}
    
    return logic


def compile_expr(expr: Any, data: Any) -> Any:
    """
    Compile an expression (PathExpr, OpExpr, or primitive) into JSONLogic or resolved value.
    
    - If expr is a PathExpr, resolve the JSONPath and return the first match (or None).
    - If expr is an OpExpr, compile recursively and return a JSONLogic dict.
    - If expr is a primitive, return it as-is.
    
    Example:
        Given: CAPITALIZE(SUBSTR(path("$..name"), 0, 10))
        Returns: {"capitalize": [{"substr": ["John Doe", 0, 10]}]}
        
        Given: PathExpr("$..name") on data {"name": "John"}
        Returns: "John"
    """
    # Handle PathExpr - resolve JSONPath immediately
    if isinstance(expr, PathExpr):
        compiled = parse(expr.jsonpath)
        matches = compiled.find(data)
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0].value
        return [m.value for m in matches]
    
    # Handle OpExpr - compile to JSONLogic dict
    if isinstance(expr, OpExpr):
        # Compile each argument recursively
        compiled_args = []
        for arg in expr.args:
            if isinstance(arg, (PathExpr, OpExpr)):
                # Recursively compile nested expressions
                compiled_arg = compile_expr(arg, data)
                compiled_args.append(compiled_arg)
            elif callable(arg):
                # Call functions to get their result
                result = arg(data)
                compiled_args.append(result)
            else:
                # Primitive value
                compiled_args.append(arg)
        
        # Return JSONLogic dict
        return {expr.op: compiled_args}
    
    # Handle primitives
    if expr is None or isinstance(expr, (int, float, str, bool)):
        return expr
    
    # Handle lists
    if isinstance(expr, list):
        return [compile_expr(item, data) for item in expr]
    
    # Handle callables (functions like path() that return expressions)
    if callable(expr):
        result = expr(data)
        return compile_expr(result, data)
    
    return expr
