"""
Expression Constructor: Converts nested logic to JSONLogic rules.
"""
from typing import Any, Dict, List, Union
from jsonpath_ng import parse


def extract_data(data: Dict[str, Any], jsonpath_expr: str) -> Any:
    """Extract data from input using jsonpathng."""
    compiled = parse(jsonpath_expr)
    matches = compiled.find(data)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].value
    return [m.value for m in matches]


def JSONPATH(jsonpath_expr: str) -> Dict[str, str]:
    """Create a JSONLogic rule that extracts data via JSONPath."""
    return {"JSONPATH": [jsonpath_expr]}


def CAPITALIZE(source: Any) -> Dict[str, Any]:
    """Create a JSONLogic CAPITALIZE rule."""
    return {"CAPITALIZE": [source]}


def SUBSTR(start: int, length: int, source: Any) -> Dict[str, Any]:
    """Create a JSONLogic SUBSTR rule."""
    return {"SUBSTR": [start, length, source]}


def JOIN_PARTS(*parts: Any) -> Dict[str, Any]:
    """Create a JSONLogic JOIN_PARTS rule."""
    return {"JOIN_PARTS": list(parts)}


def GST_DETAILS_ALL(source: Any = None) -> Dict[str, Any]:
    """Create a JSONLogic GST_DETAILS_ALL rule."""
    if source is None:
        return {"GST_DETAILS_ALL": []}
    return {"GST_DETAILS_ALL": [source]}


def to_jsonlogic(nested_expr: Any) -> Any:
    """Convert nested Python expressions to JSONLogic format."""
    if isinstance(nested_expr, dict):
        return nested_expr
    elif isinstance(nested_expr, str):
        return nested_expr
    elif isinstance(nested_expr, int):
        return nested_expr
    elif isinstance(nested_expr, float):
        return nested_expr
    elif isinstance(nested_expr, list):
        return [to_jsonlogic(item) for item in nested_expr]
    elif hasattr(nested_expr, '__jsonlogic__'):
        return nested_expr.__jsonlogic__()
    else:
        return str(nested_expr)


class ExpressionConstructor:
    """Constructs JSONLogic rules from nested expressions."""
    
    @staticmethod
    def construct(nested_expr: Any) -> Dict[str, Any]:
        """Convert nested expression to JSONLogic rule."""
        return to_jsonlogic(nested_expr)
    
    @staticmethod
    def apply(rule: Dict[str, Any], data: Dict[str, Any]) -> Any:
        """Apply JSONLogic rule to data using the jsonlogic library."""
        from src.jsonlogic_operations import apply_jsonlogic
        return apply_jsonlogic(rule, data)