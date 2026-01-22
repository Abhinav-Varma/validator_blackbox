from dataclasses import dataclass
from typing import Any, Callable, List


@dataclass(frozen=True)
class Path:
    """
    Represents a JSONPath expression.
    This is metadata only – no IO, no execution.
    """
    expr: str


@dataclass(frozen=True)
class Call:
    """
    Represents a function call in the transformation graph.
    """
    fn: Callable
    args: List[Any]


def call(fn: Callable, *args: Any) -> Call:
    return Call(fn=fn, args=list(args))
