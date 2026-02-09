# Validator Blackbox

A declarative Python framework for transforming raw JSON documents into validated, structured Pydantic models using **JSONLogic**.

---

## 🎯 Overview

**Validator Blackbox** uses the [python-jsonlogic](https://jsonlogic.readthedocs.io/) library to process transformation rules. Instead of writing imperative parsing code, you declare transformations using composable expression builders. The framework handles execution, precedence, and type safety.

---

## 🏗️ Architecture

```
rules.py → Expression Builders → JSONLogic Rule Dict → python-jsonlogic Engine → Result
```

### Pipeline Flow

```
Input Data
    ↓
TransformBaseModel.__init__()
    ↓
ExpressionConstructor.apply()
    ↓
JSONLogicExpression.from_json()
    ↓
as_operator_tree(operator_registry)
    ↓
evaluate(tree, data=data)
    ↓
Validated Model Instance
```

---

## 📁 Project Structure

```
validator_blackbox/
├── src/
│   ├── rules.py                    # User-defined Models & Transform definitions
│   ├── jsonlogic_operations.py     # Custom operators + expression builders
│   ├── expression_constructor.py    # JSONLogic engine wrapper
│   ├── custom_basemodel.py         # Pydantic BaseModel integration
│   ├── custom_types.py             # Custom strict types
│   ├── gstin_state_codes_india.json # Reference data
│   └── main.py                     # Entry point runner
├── tests/
│   └── test_all.py                 # Comprehensive tests
├── sample.json                     # Sample input data
└── requirements.txt                # Dependencies
```

---

## 🔧 Key Components

### 1. Expression Builders ([`jsonlogic_operations.py`](src/jsonlogic_operations.py))

Create JSONLogic rule dictionaries from Python expressions:

```python
# These functions return dictionaries like {"JSONPATH": ["$.name"]}
def JSONPATH(expr: str) -> dict: return {"JSONPATH": [expr]}
def CAPITALIZE(src: Any) -> dict: return {"CAPITALIZE": [src]}
def SUBSTR(start: int, length: int, src: Any) -> dict: return {"SUBSTR": [start, length, src]}
def JOIN_PARTS(*parts: Any) -> dict: return {"JOIN_PARTS": list(parts)}
def GST_DETAILS_ALL(src: Any = None) -> dict: return {"GST_DETAILS_ALL": [src] if src else []}
```

### 2. Custom Operators ([`jsonlogic_operations.py`](src/jsonlogic_operations.py))

Operator classes extending `jsonlogic.core.Operator`:

```python
@dataclass
class _JSONPATH(Operator):
    expr: str = field(default="")
    
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, expr=args[0])
    
    def evaluate(self, context):
        from jsonpath_ng import parse
        matches = parse(self.expr).find(context.data_stack.tail[0])
        return matches[0].value if len(matches) == 1 else [m.value for m in matches] or None
```

### 3. Expression Constructor ([`expression_constructor.py`](src/expression_constructor.py))

Wrapper around python-jsonlogic library:

```python
class ExpressionConstructor:
    def apply(self, rule: Dict[str, Any], data: Dict[str, Any]) -> Any:
        expr = JSONLogicExpression.from_json(rule)
        tree = expr.as_operator_tree(operator_registry)
        return evaluate(tree, data=data, data_schema=None)
```

### 4. Auto-Registration

Importing `jsonlogic_operations` triggers automatic operator registration:

```python
# Lines 81-85: Top-level code executes on import
operator_registry.register("JSONPATH", _JSONPATH)
operator_registry.register("CAPITALIZE", _CAPITALIZE)
operator_registry.register("SUBSTR", _SUBSTR)
operator_registry.register("JOIN_PARTS", _JOIN_PARTS)
operator_registry.register("GST_DETAILS_ALL", _GST_DETAILS_ALL)
```

---

## 📖 Usage

### 1. Define Transformations

In [`rules.py`](src/rules.py), use expression builders:

```python
from src.custom_basemodel import TransformBaseModel, Field
from src.jsonlogic_operations import JSONPATH, CAPITALIZE, SUBSTR, JOIN_PARTS

class UserProfile(TransformBaseModel):
    # Extract name and capitalize
    display_name: str = Field(
        transform=JOIN_PARTS(
            CAPITALIZE(JSONPATH("$..first_name")),
            " ",
            CAPITALIZE(JSONPATH("$..surname")),
        ),
    )
```

### 2. Run the Validator

```python
data = {"user": {"first_name": "paul", "surname": "smith"}}
model = UserProfile(**data)
print(model.display_name)  # Output: "Paul Smith"
```

---

## 📊 How It Works

### Step 1: Expression Builders Create JSONLogic Rule

```python
# Input:
JOIN_PARTS(
    CAPITALIZE(JSONPATH("$..first_name")),
    " ",
    CAPITALIZE(JSONPATH("$..surname")),
)

# Output (JSONLogic rule dictionary):
{
    "JOIN_PARTS": [
        {"CAPITALIZE": [{"JSONPATH": ["$..first_name"]}]},
        " ",
        {"CAPITALIZE": [{"JSONPATH": ["$..surname"]}]}
    ]
}
```

### Step 2: as_operator_tree() Builds Operator Tree

```python
# Input: JSONLogic rule dict
rule = {
    "JOIN_PARTS": [
        {"CAPITALIZE": [{"JSONPATH": ["$..first_name"]}]},
        " ",
        {"CAPITALIZE": [{"JSONPATH": ["$..surname"]}]}
    ]
}

# Output: Operator tree
_JOIN_PARTS(
    operator="JOIN_PARTS",
    parts=[
        _CAPITALIZE(src=_JSONPATH(expr="$..first_name")),
        " ",
        _CAPITALIZE(src=_JSONPATH(expr="$..surname"))
    ]
)
```

### Step 3: evaluate() Executes with Data

```python
# Input data
data = {"first_name": "paul", "surname": "smith"}

# Execution:
1. JOIN_PARTS.evaluate(context)
2. For each part:
   - CAPITALIZE.evaluate() → calls JSONPATH.evaluate()
   - JSONPATH.parse("$..first_name").find(data) → "paul"
   - CAPITALIZE returns "Paul"
3. JOIN_PARTS joins: "Paul" + " " + "Smith"
# Output: "Paul Smith"
```

---

## 🧪 Examples

### Complex Path Extraction

```python
class TravelInfoModel(TransformBaseModel):
    travel_summary: str = Field(
        transform=JOIN_PARTS(
            JSONPATH("$.visa_request_information.visa_request.from_country_full_name"),
            " → ",
            JSONPATH("$.visa_request_information.visa_request.to_country_full_name"),
            " (",
            JSONPATH("$.visa_request_information.visa_request.departure_date_formatted"),
            " to ",
            JSONPATH("$.visa_request_information.visa_request.arrival_date_formatted"),
            ")",
        ),
    )
```

**Input:**
```json
{
  "visa_request_information": {
    "visa_request": {
      "from_country_full_name": "India",
      "to_country_full_name": "Taiwan",
      "departure_date_formatted": "01-Mar-2026",
      "arrival_date_formatted": "07-Mar-2026"
    }
  }
}
```

**Output:** `India → Taiwan (01-Mar-2026 to 07-Mar-2026)`

---

### Substring and Capitalize

```python
class CustomerNameModel(TransformBaseModel):
    display_name: str = Field(
        transform=JOIN_PARTS(
            CAPITALIZE(SUBSTR(0, 10, JSONPATH("$..first_name"))),
            " ",
            CAPITALIZE(SUBSTR(0, 7, JSONPATH("$..surname"))),
        ),
    )
```

**Input:**
```json
{
  "first_name": "PAULSTALIN JOONIS EVANS",
  "surname": "GODFREY PREM KIRUBA SEKAR"
}
```

**Output:** `Paulstalin Godfrey`

---

### GST Processing

```python
class CustomerProfileModel(TransformBaseModel):
    gst_outputs: List[Dict[str, str]] = Field(
        default=[],
        transform=GST_DETAILS_ALL(JSONPATH("$.gst_records")),
    )
```

**Input:**
```json
{
  "gst_records": [
    {"gst_number": "29ABCDE1234F1Z5"},
    {"gst_number": "27PQRSX5678L1Z3"}
  ]
}
```

**Output:**
```python
[
    {'gst_number': '29ABCDE1234F1Z5', 'pan_number': 'ABCDE1234F', 'state_name': 'Karnataka'},
    {'gst_number': '27PQRSX5678L1Z3', 'pan_number': 'PQRSX5678L', 'state_name': 'Maharashtra'}
]
```

---

## 🏛️ JSONLogic Rule Format

All transformations follow this JSONLogic standard format:

| Pattern | Example | Meaning |
|---------|---------|---------|
| `{"OP": [arg]}` | `{"JSONPATH": ["$.name"]}` | Single argument |
| `{"OP": [a, b, c]}` | `{"JOIN_PARTS": ["a", "b"]}` | Multiple arguments |
| `{"OP": [{"NESTED": [...]}]}` | `{"CAPITALIZE": [{"JSONPATH": [...]}]}` | Nested operator |
| `{"OP": [primitive]}` | `{"+": [1, 2]}` | Literal values |

---

## 🔌 Adding New Operators

### 1. Define Operator Class

```python
# In jsonlogic_operations.py
from dataclasses import dataclass, field
from jsonlogic.core import Operator

@dataclass
class REVERSE(Operator):
    src: Any = field(default=None)
    
    @classmethod
    def from_expression(cls, op: str, args):
        return cls(operator=op, src=args[0])
    
    def evaluate(self, context):
        val = self.src
        if isinstance(val, Operator): val = val.evaluate(context)
        return None if val is None else str(val)[::-1]
```

### 2. Register Operator

```python
# At module level (auto-registers on import)
operator_registry.register("REVERSE", REVERSE)
```

### 3. Create Expression Builder

```python
def REVERSE(src: Any) -> dict:
    return {"REVERSE": [src]}
```

### 4. Use in Rules

```python
from src.jsonlogic_operations import REVERSE

class MyModel(TransformBaseModel):
    reversed_name: str = Field(
        transform=REVERSE(JSONPATH("$..name")),
    )
```

---

## 🧪 Running Tests

```bash
PYTHONPATH=/home/dreamworld/GitHub/validator_blackbox python tests/test_all.py
```

---

## 📦 Dependencies

- **pydantic** - Data validation
- **jsonpath-ng** - JSONPath expressions
- **python-jsonlogic** - JSONLogic evaluation
- **python-json-schema** - Type checking (via jsonlogic)

---

## 📄 License

MIT
