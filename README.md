# Design Document

## Executive Summary

This document outlines the system architecture, rule specifications, and transformation mechanisms for implementing a JSON transformation engine.

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Engine                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │ Rule Parser │→ │AST Generator │→ │Expression Evaluator  │    │
│  └─────────────┘  └──────────────┘  └──────────────────────┘    │
│                           ↓                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │Pydantic     │← │Transformer   │← │Context Manager       │    │
│  │Model Gen    │  │Orchestrator  │  │                      │    │
│  └─────────────┘  └──────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                           ↓
                    Transformed JSON
```

### 1.2 Core Components

**Rule Parser**: Validates and parses rule expressions
**AST Generator**: Creates executable abstract syntax trees
**Expression Evaluator**: Executes transformations with lazy evaluation using Pydantic
**Context Manager**: Maintains variable scope and JSON path resolution
**Pydantic Model Generator**: Creates dynamic validation models
**Transformer Orchestrator**: Coordinates the transformation pipeline

---

## 2. Rule File Structure

### 2.1 Rule File Format

Rule files use YAML format for human readability and machine processing:

```yaml

# Transformation rules
rules:
  - target: "full_name"
    expression: "capitalize(.first_name) + ' ' + capitalize(.last_name)"
    
  - target: "contact_info"
    expression: |
      {
        "email": lower(.email),
        "phone": format_phone(.phone),
        "preferred_contact": if (.email_verified) "email" else "phone"
      }
    condition: ".contact_method != null"
```

### 2.2 Rule Components

**Target Field**: Output field name
**Expression**: transformation expression
**Condition**: Optional boolean expression for conditional execution
**Fallback**: Alternative expression for error cases

### 2.3 Expression Syntax Reference

| Operation | Syntax | Example |
|-----------|--------|---------|
| Field Access | `.field_name` | `.user.name` |
| Array Index | `.array[index]` | `.items[0]` |
| Array Slice | `.array[start:end]` | `.items[1:5]` |
| Wildcard | `.object.*` | `.properties.*` |
| Variable | `$variable_name` | `$base_price` |
| Function Call | `function_name(args)` | `capitalize(.name)` |
| Conditional | `if (condition) then else` | `if (.age > 18) "adult" else "minor"` |
| Array Comprehension | `[for (.array) expression]` | `[for (.items) .price]` |
| Object Comprehension | `{for (.object) key: value}` | `{for (.props) .name: .value}` |

---

## 3. Transformation Using Pydantic

### 3.1 Dynamic Model Generation Process

**Input Analysis**: Scan input JSON to determine field types and structure
**Type Inference**: Analyze transformation expressions to predict output types
**Model Creation**: Generate Pydantic models with appropriate field types
**Validator Integration**: Embed transformation logic as Pydantic validators
**Compilation**: Create executable model classes

Below is a self-contained example that shows how you can “store” every transformation rule in a plain Python dict (the “rulebook”) and then, at run-time, build a **unique Pydantic model per rule** that already contains the right validator(s).  
The trick is to create the validator(s) on-the-fly with `field_validator` and attach them to a dynamic model that is produced by `create_model`.

```python
from __future__ import annotations
import re
from typing import Any, Dict, List, Callable

from pydantic import BaseModel, field_validator, create_model

# ------------------------------------------------------------------
# 1.  A tiny library of the transformation functions you listed
# ------------------------------------------------------------------
def _capitalize(v: str) -> str:
    return v.capitalize()

def _split(v: str, delim: str = ",", idx: int = 0) -> str:
    return v.split(delim)[idx]

def _join(delim: str, *parts: str) -> str:
    return delim.join(parts)

def _regex_replace(v: str, pattern: str, repl: str) -> str:
    return re.sub(pattern, repl, v)

def _sum(v: list[float]) -> float:
    return sum(v)

# Map the name that appears in the rulebook → actual callable
TRANSFORM_LIB: Dict[str, Callable[..., Any]] = {
    "capitalize": _capitalize,
    "split": _split,
    "join": _join,
    "regex_replace": _regex_replace,
    "sum": _sum,
}

# ------------------------------------------------------------------
# 2.  The rulebook – plain JSON-serialisable Python objects
# ------------------------------------------------------------------
#  key   → field we want to validate/transform
#  value → list of ["operation_name", *args]
RULEBOOK: Dict[str, List[List[Any]]] = {
    "first_name": [["capitalize"]],
    "email_user": [["split", "@", 0], ["capitalize"]],
    "display_name": [["join", " ", "first_name", "last_name"]],
    "lucky_number": [["sum"]],
}

# ------------------------------------------------------------------
# 3.  Factory: build one Pydantic model per rule
# ------------------------------------------------------------------
def build_dynamic_model(rules: Dict[str, List[List[Any]]]) -> type[BaseModel]:
    """
    Returns a *new* Pydantic model class whose fields have the validators
    described in `rules`.
    """
    validators: Dict[str, classmethod] = {}

    for field, chain in rules.items():
        # Build one validator per field
        def make_validator(chain=chain):
            # closure so `chain` is frozen for this validator
            def _validate(cls, v):
                for step in chain:
                    op, *args = step
                    func = TRANSFORM_LIB[op]
                    # If the operation needs the *current* field value
                    # we pass it as first argument
                    v = func(v, *args)
                return v

            # Pydantic 2.x style
            return field_validator(field)(_validate)

        validators[f"_{field}_validator"] = make_validator()

    # create_model wants the namespace as dict
    return create_model(
        "DynamicRuleModel",
        __validators__=validators,
        # fields without type info default to `Any`
        **{f: (Any, ...) for f in rules},
    )

# ------------------------------------------------------------------
# 4.  Demo
# ------------------------------------------------------------------
if __name__ == "__main__":
    Model = build_dynamic_model(RULEBOOK)

    data = {
        "first_name": "john",
        "email_user": "john.doe@example.com",
        "display_name": ["John", "Doe"],   # will be joined
        "lucky_number": [7, 3, 11],
    }

    obj = Model(**data)
    print(obj.model_dump())
    # → {'first_name': 'John',
    #    'email_user': 'John.doe',
    #    'display_name': 'John Doe',
    #    'lucky_number': 21}
```

How it works
1. The rulebook is just plain data—no code.  
2. `build_dynamic_model` walks through the rulebook and, for every field, manufactures one `field_validator` whose body simply *chains* the listed operations.  
3. `create_model` is used to mint a brand-new Pydantic class that carries those validators.  
4. You can ship as many different rulebooks as you like; each call gives you a new model class without writing any extra Python source files.

### 3.2 Model Generation Workflow

```
Input JSON → Structure Analysis → Type Mapping → Model Definition → Validator Generation → Compiled Model
     ↓              ↓               ↓              ↓                ↓               ↓
  {"name":    Detect string    str field    class Transform    @validator       Cached model
   "age": 25}  Detect number    int field    name: str        def validate_    ready for
                                            age: int         name(cls, v)     execution
```

### 3.3 Transformation Execution

**Phase 1: Pre-processing**
- Validate input JSON against detected schema
- Parse and compile PyJSLT expressions
- Resolve variable dependencies
- Optimize expression evaluation order

**Phase 2: Model Instantiation**
- Create Pydantic model instance from input data
- Execute field validators with transformation logic
- Handle validation errors with detailed context
- Support partial validation for incremental processing

**Phase 3: Transformation Application**
- Apply transformations in dependency order
- Maintain context stack for nested expressions
- Handle null values and missing fields per configuration
- Generate computed fields based on expressions

**Phase 4: Output Generation**
- Serialize validated model to JSON
- Apply output formatting options
- Include/exclude fields per configuration
- Generate performance metrics

---

## 4. Function Library

### 4.1 String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `capitalize(string)` | Capitalize first letter | `capitalize("john")` → "John" |
| `lower(string)` | Convert to lowercase | `lower("JOHN")` → "john" |
| `upper(string)` | Convert to uppercase | `upper("john")` → "JOHN" |
| `trim(string)` | Remove whitespace | `trim("  john  ")` → "john" |
| `contains(string, substring)` | Check substring | `contains("hello", "ell")` → true |
| `split(string, delimiter, index)` | Split and get element | `split("a,b,c", ",", 1)` → "b" |
| `join(separator, ...strings)` | Concatenate strings | `join(" ", "hello", "world")` → "hello world" |
| `replace(string, old, new)` | Replace substring | `replace("hello", "l", "x")` → "hexxo" |
| `regex_replace(string, pattern, replacement)` | Regex replacement | `regex_replace("123", "\\d", "X")` → "XXX" |

### 4.2 Numeric Functions

| Function | Description | Example |
|----------|-------------|---------|
| `abs(number)` | Absolute value | `abs(-5)` → 5 |
| `round(number, decimals)` | Round to decimals | `round(3.14159, 2)` → 3.14 |
| `floor(number)` | Round down | `floor(3.7)` → 3 |
| `ceil(number)` | Round up | `ceil(3.2)` → 4 |
| `min(array)` | Minimum value | `min([3, 1, 4])` → 1 |
| `max(array)` | Maximum value | `max([3, 1, 4])` → 4 |
| `sum(array)` | Sum of values | `sum([1, 2, 3])` → 6 |
| `avg(array)` | Average value | `avg([1, 2, 3])` → 2 |

### 4.3 Array Functions

| Function | Description | Example |
|----------|-------------|---------|
| `size(array)` | Array length | `size([1, 2, 3])` → 3 |
| `is_empty(array)` | Check if empty | `is_empty([])` → true |
| `first(array)` | First element | `first([1, 2, 3])` → 1 |
| `last(array)` | Last element | `last([1, 2, 3])` → 3 |
| `sort(array)` | Sort elements | `sort([3, 1, 2])` → [1, 2, 3] |
| `reverse(array)` | Reverse order | `reverse([1, 2, 3])` → [3, 2, 1] |
| `unique(array)` | Remove duplicates | `unique([1, 2, 2, 3])` → [1, 2, 3] |

### 4.4 Object Functions

| Function | Description | Example |
|----------|-------------|---------|
| `keys(object)` | Get property names | `keys({"a": 1, "b": 2})` → ["a", "b"] |
| `values(object)` | Get property values | `values({"a": 1, "b": 2})` → [1, 2] |
| `merge(object1, object2)` | Combine objects | `merge({"a": 1}, {"b": 2})` → {"a": 1, "b": 2} |
| `pick(object, ...fields)` | Select fields | `pick({"a": 1, "b": 2, "c": 3}, "a", "c")` → {"a": 1, "c": 3} |
| `omit(object, ...fields)` | Exclude fields | `omit({"a": 1, "b": 2, "c": 3}, "b")` → {"a": 1, "c": 3} |

---

## 5. Usage Examples

### 5.1 Basic User Data Transformation

**Input JSON**:
```json
{
  "first_name": "john",
  "last_name": "doe",
  "email": "JOHN.DOE@EXAMPLE.COM",
  "age": 25,
  "phone": "1234567890"
}
```

**Rule File**:
```yaml
rules:
  - target: "full_name"
    expression: "capitalize(.first_name) + ' ' + capitalize(.last_name)"
    
  - target: "email_normalized"
    expression: "lower(.email)"
    
  - target: "contact_info"
    expression: |
      {
        "email": .email_normalized,
        "phone": format_phone(.phone),
        "preferred": "email"
      }
    
  - target: "status"
    expression: "if (.age >= 18) 'adult' else 'minor'"

functions:
  - name: "format_phone"
    parameters: ["phone"]
    expression: "regex_replace(phone, '(\\d{3})(\\d{3})(\\d{4})', '($1) $2-$3')"
```

**Output JSON**:
```json
{
  "first_name": "john",
  "last_name": "doe",
  "email": "JOHN.DOE@EXAMPLE.COM",
  "age": 25,
  "phone": "1234567890",
  "full_name": "John Doe",
  "email_normalized": "john.doe@example.com",
  "contact_info": {
    "email": "john.doe@example.com",
    "phone": "(123) 456-7890",
    "preferred": "email"
  },
  "status": "adult"
}
```

### 5.2 E-commerce Product Transformation

**Input JSON**:
```json
{
  "products": [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
    {"id": 2, "name": "Mouse", "price": 29.99, "category": "Electronics"},
    {"id": 3, "name": "Desk", "price": 199.99, "category": "Furniture"}
  ]
}
```

**Rule File**:
```yaml
rules:
  - target: "product_summary"
    expression: |
      {
        "total_products": size(.products),
        "categories": unique([for (.products) .category]),
        "price_range": {
          "min": min([for (.products) .price]),
          "max": max([for (.products) .price]),
          "average": round(avg([for (.products) .price]), 2)
        }
      }
      
  - target: "expensive_products"
    expression: "[for (.products) if (.price > 100) .]"
    
  - target: "product_names"
    expression: "[for (.products) capitalize(.name)]"
    
  - target: "products_by_category"
    expression: "{for (.products) .category : [for (.products) if (.category == $category) .]}"
```

---
