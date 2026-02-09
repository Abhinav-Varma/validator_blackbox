"""
Expression Constructor: JSONLogic framework using python-jsonlogic library.
"""
from typing import Any, Dict, Optional
from jsonlogic import JSONLogicExpression
from jsonlogic.evaluation import evaluate
from jsonlogic.operators import operator_registry

class ExpressionConstructor:
    def __init__(self, registry: Optional[Any] = None):
        pass
    
    def construct(self, nested_expr: Any) -> Dict[str, Any]:
        """Convert nested expression to JSONLogic rule."""
        return nested_expr if isinstance(nested_expr, dict) else nested_expr
    
    def apply(self, rule: Dict[str, Any], data: Dict[str, Any]) -> Any:
        """Apply JSONLogic rule to data using python-jsonlogic library."""
        expr = JSONLogicExpression.from_json(rule)
        tree = expr.as_operator_tree(operator_registry)
        return evaluate(tree, data=data, data_schema=None)

# Compatibility functions
def get_registry():
    """Get the default operator registry from python-jsonlogic."""
    return operator_registry

def get_engine():
    """Get an engine wrapper (returns ExpressionConstructor for compatibility)."""
    return ExpressionConstructor()


