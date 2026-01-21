from typing import Dict, Any, Optional
import re
from jsonpath_ng import parse
from src.function_pool import GST_DETAILS_FOR
from src.function_pool import (
    CONCATENATE,
    CAPITALIZE,
    JOIN,
    SUBSTR,
    GST_STATE_NAME,
)

FUNCTIONS = {
    "CONCATENATE": CONCATENATE,
    "CAPITALIZE": CAPITALIZE,
    "JOIN": JOIN,
    "SUBSTR": SUBSTR,
    "GST_DETAILS_FOR": GST_DETAILS_FOR,
    "GST_STATE_NAME": GST_STATE_NAME,
}

FORBIDDEN_TOKENS = [
    "__", "import", "eval", "exec", "open",
    "globals", "locals", "lambda", "class",
    "os.", "sys.", "subprocess"
]


def transformer(logic: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
    # Basic guardrail
    for token in FORBIDDEN_TOKENS:
        if token in logic:
            raise ValueError(f"Forbidden token in expression: {token}")

    if json_data is None:
        safe_globals = {"__builtins__": {}}
        exec_context = {**FUNCTIONS}
        exec(f"output = {logic}", safe_globals, exec_context)
        return exec_context["output"]

    jsonpath_pattern = r'\$[^),\s]+'
    modified_logic = logic

    jsonpath_matches = re.findall(jsonpath_pattern, logic)

    for jsonpath_expr in set(jsonpath_matches):
        try:
            parser = parse(jsonpath_expr)
            matches = parser.find(json_data)
            if matches:
                value = matches[0].value

                if isinstance(value, str):
                    replacement = f"'{value}'"
                else:
                    # lists / dicts / numbers → inject as Python literal
                    replacement = repr(value)

                modified_logic = modified_logic.replace(
                    jsonpath_expr, replacement
                )
            else:
                modified_logic = modified_logic.replace(
                    jsonpath_expr, "''"
                )
        except Exception:
            modified_logic = modified_logic.replace(
                jsonpath_expr, "''"
            )

    safe_globals = {"__builtins__": {}}
    exec_context = {**FUNCTIONS}
    exec(f"output = {modified_logic}", safe_globals, exec_context)
    return exec_context["output"]
