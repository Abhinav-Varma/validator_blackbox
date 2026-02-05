# custom_types.py
from pydantic_core import core_schema


class NonEmptyStr(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("must be a non-empty string")
        return cls(value)


class PassportNumber(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(min_length=6, max_length=9),
        )

    @classmethod
    def _validate(cls, value: str):
        if not value.isalnum():
            raise ValueError("passport number must be alphanumeric")
        return cls(value.upper())


class Expr:
    """Base expression type.

    The pipeline/operator-overload support (using `|`) was removed because
    the codebase uses nested function-call style transforms. If you need
    pipeline-style syntax again, reintroduce an explicit implementation
    and add tests to cover it.
    """
    pass


class PathExpr(Expr):
    def __init__(self, jsonpath: str):
        self.jsonpath = jsonpath
        from jsonpath_ng import parse
        # Cache compiled JSONPath to avoid reparsing on every call
        self._compiled = parse(jsonpath)

    def __call__(self, data):
        matches = self._compiled.find(data)
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0].value
        return [m.value for m in matches]


class OpExpr(Expr):
    def __init__(self, op: str, args: list):
        self.op = op
        self.args = args

    def __call__(self, data):
        """Evaluate the expression with the given data."""
        # Evaluate arguments - if they are expressions, call them; otherwise use as-is
        evaluated_args = []
        for arg in self.args:
            if isinstance(arg, Expr):
                evaluated_args.append(arg(data))
            elif callable(arg):
                evaluated_args.append(arg(data))
            else:
                evaluated_args.append(arg)
        
        # Now execute the operation
        return self._execute(evaluated_args, data)
    
    def _execute(self, args, data=None):
        """Delegate execution to shared functions in `function_pool`."""
        from src.function_pool import execute
        return execute(self.op, args, data)
