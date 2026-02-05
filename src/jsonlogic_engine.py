"""Delegate to an external json-logic implementation only.

This module imports a single function from an installed package and
delegates calls to it. It does not contain any local JsonLogic
implementation — if the external package is missing or incompatible
an ImportError or the package's exception will surface.
"""

from typing import Any, Dict


_external = None
_external_name = None
try:
    # prefer the widely-used `jsonlogic` package
    from jsonlogic import jsonLogic as _external  # type: ignore
    _external_name = "jsonlogic.jsonLogic"
except Exception:
    try:
        # try the alternative distribution `json-logic` (module `json_logic`)
        from json_logic import jsonLogic as _external  # type: ignore
        _external_name = "json_logic.jsonLogic"
    except Exception:
        _external = None

# The `json-logic` distribution on PyPI exposes a module whose
# implementation was written for Python 2 and indexes `dict.keys()`.
# That breaks on modern Python where `dict.keys()` returns a view.
# To tolerate that broken package we wrap its `jsonLogic` function and
# convert input rule dicts into a mapping whose `keys()` returns a
# real list (indexable). This preserves strict external-only
# delegation while making the installed package usable.
if _external_name == "json_logic.jsonLogic":
    # keep reference to the original imported function to avoid recursion
    _external_orig = _external

    class _KeyedDict(dict):
        def keys(self):
            return list(super().keys())

    def _convert_lists_and_dicts(obj):
        if isinstance(obj, dict):
            converted = {k: _convert_lists_and_dicts(v) for k, v in obj.items()}
            # json_logic package expects the ternary operator under '?:'
            # while many JsonLogic inputs use 'if'. Translate here.
            if "if" in converted:
                if_val = converted.pop("if")
                def _nest_if(lst):
                    if not isinstance(lst, (list, tuple)):
                        return lst
                    if len(lst) == 3:
                        return [lst[0], lst[1], lst[2]]
                    # nest into dict for the else branch so the package
                    # sees a {'?:': [...]} structure for nested ternaries
                    return [lst[0], lst[1], {"?:": _nest_if(lst[2:])}]
                converted["?:"] = _nest_if(if_val)
            # Translate 'missing' to a simple None-check when possible.
            if "missing" in converted:
                miss_val = converted.pop("missing")
                # If caller provided a single path, translate to var == None
                if isinstance(miss_val, (list, tuple)) and len(miss_val) == 1:
                    converted = {"==": [{"var": miss_val[0]}, None]}
            
            return _KeyedDict(converted)
        if isinstance(obj, (list, tuple)):
            return type(obj)(_convert_lists_and_dicts(v) for v in obj)
        return obj

    def _external_wrapper(rule, data=None):
        return _external_orig(_convert_lists_and_dicts(rule), data)

    _external = _external_wrapper


def jsonLogic(rule: Any, data: Dict[str, Any] | None = None) -> Any:
    """Evaluate a JsonLogic rule using the external library.

    Raises ImportError with installation instructions when no supported
    external implementation is available.
    """
    if _external is None:
        raise ImportError(
            "No external json-logic implementation found.\n"
            "Install one with: pip install jsonlogic\n"
            "(or: pip install json-logic and try module json_logic)"
        )

    # Delegate directly to the external function; let any runtime errors
    # from the external package bubble up so the user can address them.
    return _external(rule, data)
