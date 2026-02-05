"""
JSONLogic compiler and execution engine.
"""
from typing import Any, Dict, List, Union

from jsonpath_ng import parse

from src.custom_types import PathExpr, OpExpr
from src.function_pool import KNOWN_OPERATORS, execute


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
                
                # Delegate operator execution to shared dispatcher
                return execute(op, evaluated_args, data)
        
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
