"""
JSONLogic Operations: Custom operations for the jsonlogic library.
"""
from typing import Any, Dict, List
import json
import pathlib
from dataclasses import field
from jsonlogic.core import Operator, OperatorArgument
from jsonlogic.registry import OperatorRegistry
from jsonlogic.evaluation import EvaluationContext


# Load GST state code map
_GST_MAP_PATH = pathlib.Path(__file__).with_name("gstin_state_codes_india.json")
GST_STATE_CODE_MAP: Dict[str, str] = json.loads(_GST_MAP_PATH.read_text())


class JsonPathOperator(Operator):
    """JSONPATH operator using jsonpathng."""
    _operator: str = field(init=False, repr=False)
    _arguments: list = field(init=False, repr=False)
    
    def __init__(self, operator: str, arguments: list[OperatorArgument]):
        self._operator = operator
        self._arguments = arguments
    
    @property
    def operator(self) -> str:
        return self._operator
    
    @classmethod
    def from_expression(cls, operator: str, arguments: list[OperatorArgument]):
        if len(arguments) != 1:
            raise ValueError("JSONPATH requires exactly 1 argument")
        return cls(operator, arguments)
    
    def evaluate(self, context: EvaluationContext) -> Any:
        from jsonpath_ng import parse
        # Get the JSONPath expression from arguments
        jsonpath_expr = self._arguments[0]
        if isinstance(jsonpath_expr, str):
            # It's a literal string, use it directly
            compiled = parse(jsonpath_expr)
            # Get root data from data_stack
            data = context.data_stack.tail[0]
            matches = compiled.find(data)
            if not matches:
                return None
            if len(matches) == 1:
                return matches[0].value
            return [m.value for m in matches]
        else:
            # It's another operator, evaluate it first
            if isinstance(jsonpath_expr, Operator):
                return jsonpath_expr.evaluate(context)
            return jsonpath_expr


class CapitalizeOperator(Operator):
    """CAPITALIZE operator."""
    _operator: str = field(init=False, repr=False)
    _arguments: list = field(init=False, repr=False)
    
    def __init__(self, operator: str, arguments: list[OperatorArgument]):
        self._operator = operator
        self._arguments = arguments
    
    @property
    def operator(self) -> str:
        return self._operator
    
    @classmethod
    def from_expression(cls, operator: str, arguments: list[OperatorArgument]):
        if len(arguments) != 1:
            raise ValueError("CAPITALIZE requires exactly 1 argument")
        return cls(operator, arguments)
    
    def evaluate(self, context: EvaluationContext) -> str:
        # Get the source value from arguments
        source = self._arguments[0]
        if isinstance(source, Operator):
            value = source.evaluate(context)
        else:
            value = source
        
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        return value.capitalize()


class SubstrOperator(Operator):
    """SUBSTR operator."""
    _operator: str = field(init=False, repr=False)
    _arguments: list = field(init=False, repr=False)
    
    def __init__(self, operator: str, arguments: list[OperatorArgument]):
        self._operator = operator
        self._arguments = arguments
    
    @property
    def operator(self) -> str:
        return self._operator
    
    @classmethod
    def from_expression(cls, operator: str, arguments: list[OperatorArgument]):
        if len(arguments) != 3:
            raise ValueError("SUBSTR requires exactly 3 arguments")
        return cls(operator, arguments)
    
    def evaluate(self, context: EvaluationContext) -> str:
        # Evaluate all arguments
        start = self._arguments[0] if not isinstance(self._arguments[0], Operator) else self._arguments[0].evaluate(context)
        length = self._arguments[1] if not isinstance(self._arguments[1], Operator) else self._arguments[1].evaluate(context)
        source = self._arguments[2] if not isinstance(self._arguments[2], Operator) else self._arguments[2].evaluate(context)
        
        if source is None:
            return None
        if not isinstance(source, str):
            source = str(source)
        return source[start:start + length]


class JoinPartsOperator(Operator):
    """JOIN_PARTS operator."""
    _operator: str = field(init=False, repr=False)
    _arguments: list = field(init=False, repr=False)
    
    def __init__(self, operator: str, arguments: list[OperatorArgument]):
        self._operator = operator
        self._arguments = arguments
    
    @property
    def operator(self) -> str:
        return self._operator
    
    @classmethod
    def from_expression(cls, operator: str, arguments: list[OperatorArgument]):
        return cls(operator, arguments)
    
    def evaluate(self, context: EvaluationContext) -> str:
        # Evaluate all arguments
        result = []
        for arg in self._arguments:
            if isinstance(arg, Operator):
                value = arg.evaluate(context)
            else:
                value = arg
            
            if value is None:
                result.append("")
            elif isinstance(value, str):
                result.append(value)
            else:
                result.append(str(value))
        return "".join(result)


class GstDetailsAllOperator(Operator):
    """GST_DETAILS_ALL operator."""
    _operator: str = field(init=False, repr=False)
    _arguments: list = field(init=False, repr=False)
    
    def __init__(self, operator: str, arguments: list[OperatorArgument]):
        self._operator = operator
        self._arguments = arguments
    
    @property
    def operator(self) -> str:
        return self._operator
    
    @classmethod
    def from_expression(cls, operator: str, arguments: list[OperatorArgument]):
        return cls(operator, arguments)
    
    def evaluate(self, context: EvaluationContext) -> List[Dict[str, str]]:
        # Get the records - either from arguments (JSONPATH result) or from root data
        if self._arguments and len(self._arguments) > 0:
            records = self._arguments[0]
            if isinstance(records, Operator):
                records = records.evaluate(context)
        else:
            # No arguments, try to get gst_records from root data
            data = context.data_stack.tail[0]
            records = data.get("gst_records", [])
        
        if not records or not isinstance(records, list):
            return []
        
        # Handle nested list
        if len(records) > 0 and isinstance(records[0], list):
            records = records[0]
        
        out: List[Dict[str, str]] = []
        for rec in records:
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


# Create a registry and register custom operators
_jsonlogic_registry = OperatorRegistry()
_jsonlogic_registry.register("JSONPATH", JsonPathOperator)
_jsonlogic_registry.register("CAPITALIZE", CapitalizeOperator)
_jsonlogic_registry.register("SUBSTR", SubstrOperator)
_jsonlogic_registry.register("JOIN_PARTS", JoinPartsOperator)
_jsonlogic_registry.register("GST_DETAILS_ALL", GstDetailsAllOperator)


def apply_jsonlogic(rule: Dict[str, Any], data: Dict[str, Any]) -> Any:
    """Apply a JSONLogic rule to data using the jsonlogic library."""
    from jsonlogic import JSONLogicExpression
    
    try:
        # Create the expression from JSON
        expr = JSONLogicExpression.from_json(rule)
        
        # Convert to operator tree
        operator_tree = expr.as_operator_tree(_jsonlogic_registry)
        
        # Create evaluation context
        context = EvaluationContext(
            root_data=data,
            data_schema={},
        )
        
        # Evaluate
        result = operator_tree.evaluate(context)
        return result
    except Exception as e:
        # Fallback to simple dict return for non-expression rules
        print(f"JSONLogic evaluation error: {e}")
        return rule if isinstance(rule, dict) else rule