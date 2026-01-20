from typing import Dict
from src.function_pool import CONCATENATE, CAPITALIZE

FUNCTIONS = {
    "CONCATENATE": CONCATENATE,
    "CAPITALIZE": CAPITALIZE,
}

def transformer(logic: str) -> str:
    exec_context = {**FUNCTIONS}
    exec(f"output = {logic}", {}, exec_context)
    return exec_context['output']
