from jsonpath_ng import parse
from src.toolkit import Path, Call


def evaluate(node, json_data):
    if isinstance(node, Path):
        matches = parse(node.expr).find(json_data)
        return matches[0].value if matches else None

    if isinstance(node, Call):
        evaluated_args = [evaluate(a, json_data) for a in node.args]
        return node.fn(*evaluated_args)

    return node
