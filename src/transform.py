# src/transform.py
from typing import Dict, Any, Optional
import re
from jsonpath_ng import parse
from src.function_pool import CONCATENATE, CAPITALIZE

FUNCTIONS = {
    "CONCATENATE": CONCATENATE,
    "CAPITALIZE": CAPITALIZE,
}

def transformer(logic: str, json_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Transform logic with optional JSONPath support.
    Replaces JSONPath expressions like $..field with actual values from json_data.
    """
    if json_data is None:
        # Original behavior without JSON data
        exec_context = {**FUNCTIONS}
        exec(f"output = {logic}", {}, exec_context)
        return exec_context['output']
    
    # Find and replace JSONPath expressions
    jsonpath_pattern = r'\$[^),)\s]+'
    modified_logic = logic
    
    # Extract all JSONPath expressions
    jsonpath_matches = re.findall(jsonpath_pattern, logic)
    
    # Process each JSONPath expression
    for jsonpath_expr in set(jsonpath_matches):  # Use set to avoid duplicates
        try:
            parser = parse(jsonpath_expr)
            matches = parser.find(json_data)
            if matches:
                value = str(matches[0].value)
                # Replace JSONPath with quoted string value
                modified_logic = modified_logic.replace(jsonpath_expr, f"'{value}'")
            else:
                # If no match found, replace with empty string
                modified_logic = modified_logic.replace(jsonpath_expr, "''")
        except Exception as e:
            print(f"Warning: Could not parse JSONPath {jsonpath_expr}: {e}")
            modified_logic = modified_logic.replace(jsonpath_expr, "''")
    
    # Execute the modified logic
    exec_context = {**FUNCTIONS}
    exec(f"output = {modified_logic}", {}, exec_context)
    return exec_context['output']