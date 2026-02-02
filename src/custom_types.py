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
    def __or__(self, other: "Expr") -> "OpExpr":
        if isinstance(other, OpExpr):
            # If the other OpExpr has None as its first argument, replace it with self
            if other.args and other.args[0] is None:
                new_args = [self] + other.args[1:]
                return OpExpr(other.op, new_args)
            # Otherwise, it's a pipe operation
            return OpExpr("pipe", [self, other])
        return NotImplemented


class PathExpr(Expr):
    def __init__(self, jsonpath: str):
        self.jsonpath = jsonpath

    def __call__(self, data):
        from jsonpath_ng import parse
        compiled = parse(self.jsonpath)
        matches = compiled.find(data)
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
        return self._execute(evaluated_args)
    
    def _execute(self, args):
        """Execute the operation with evaluated arguments."""
        import json
        import pathlib
        
        if self.op == "path":
            from jsonpath_ng import parse
            jsonpath = args[0]
            compiled = parse(jsonpath)
            matches = compiled.find(args[1] if len(args) > 1 else {})
            if not matches:
                return None
            if len(matches) == 1:
                return matches[0].value
            return [m.value for m in matches]
        
        elif self.op == "capitalize":
            v = args[0]
            if v is None:
                return None
            s = v if isinstance(v, str) else str(v)
            return s.capitalize()
        
        elif self.op == "substr":
            v = args[0]
            start = args[1]
            length = args[2]
            if v is None:
                return None
            s = v if isinstance(v, str) else str(v)
            return s[start:start + length]
        
        elif self.op == "join_parts":
            return "".join(str(arg) for arg in args)
        
        elif self.op == "gst_details_all":
            records = args[0]
            _GST_MAP_PATH = pathlib.Path(__file__).parent / "gstin_state_codes_india.json"
            GST_STATE_CODE_MAP = json.loads(_GST_MAP_PATH.read_text())
            
            if records and isinstance(records, list) and len(records) > 0 and isinstance(records[0], list):
                records = records[0]
            out = []
            for rec in records if records else []:
                if not isinstance(rec, dict):
                    continue
                gst = rec.get("gst_number")
                if not isinstance(gst, str) or len(gst) < 12:
                    continue
                state_code = gst[:2]
                pan = gst[2:12]
                out.append({
                    "gst_number": gst, 
                    "pan_number": pan, 
                    "state_name": GST_STATE_CODE_MAP.get(state_code, "")
                })
            return out
        
        else:
            raise ValueError(f"Unknown operation: {self.op}")
