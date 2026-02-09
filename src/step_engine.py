"""
Typed, composable transformation steps.
NO concrete functions except `path`.
Whitelist is enforced by importing *only* from function_pool.
"""
from __future__ import annotations
from typing import TypeVar, Callable, Any, Dict, Generic

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

class Step(Generic[T, U]):
    """T -> U with left-to-right composition via |"""
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[[T], U]) -> None:
        self._fn = fn

    def __call__(self, value: T) -> U:
        return self._fn(value)

    def __or__(self, other: Step[U, V]) -> Step[T, V]:
        return Step(lambda v: other(self(v)))

# ------------------------------------------------------------------
# JSON-Path helper  (ONLY transform primitive defined here)
# ------------------------------------------------------------------
class Path(Step[Dict[str, Any], Any]):
    __slots__ = ("_path", "_compiled")

    def __init__(self, jsonpath: str) -> None:
        from jsonpath_ng import parse
        self._path = jsonpath
        self._compiled = parse(jsonpath)
        super().__init__(self._resolve)

    def _resolve(self, blob: Dict[str, Any]) -> Any:
        matches = self._compiled.find(blob)
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0].value
        return [m.value for m in matches]

path = Path  # convenience alias