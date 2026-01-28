# Validator Blackbox

A robust, declarative Python framework for transforming raw JSON documents into validated, structured Pydantic models.

**Validator Blackbox** decouples transformation logic from validation rules. Instead of writing imperative parsing code, you declare **how** each field is derived using a composable set of typed "Steps". The framework handles execution, precedence, and safety—letting you focus on the business logic.

---

## 🚀 Key Features

- **Declarative Configuration**: Define transformations inline with your Pydantic model fields using `Field(transform=...)`.
- **Flexible Composition**: Support for both **Pipe-Style** (`path(...) | OP`) and **Nested-Call** (`OP(path(...))`) syntax.
- **Type-Safe Transformation**: Every step is typed (`Step[T, U]`), ensuring clarity and editor support.
- **Secure Execution**: Only whitelisted functions from `function_pool.py` are executable. No `eval` or unsafe dynamic code.
- **Precedence Control**: Transformed values automatically override input data (when successful), ensuring your business rules always apply.
- **JSONPath Integration**: Built-in support for extracting data deep within complex JSON structures.

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/validator_blackbox.git
   cd validator_blackbox
   ```

2. **Install dependencies** (virtual environment recommended):
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Usage

### 1. Define your Transformations
Usage is centered around `rules.py`. Import helpers from the `function_pool` and assign them to `transform` in your model fields.

**Pipe Style** (Left-to-Right reading flow):
```python
from src.rules import TransformBaseModel, Field
from src.step_engine import path
from src.function_pool import CAPITALIZE, SUBSTR

class UserProfile(TransformBaseModel):
    # Extract 'name', take first 10 chars, then capitalize
    display_name: str = Field(
        transform=path("$.user.name") | SUBSTR(0, 10) | CAPITALIZE()
    )
```

**Nested-Call Style** (Functional reading flow):
```python
class UserProfile(TransformBaseModel):
    # Same logic, written functionally
    display_name: str = Field(
        transform=CAPITALIZE(SUBSTR(0, 10, path("$.user.name")))
    )
```

### 2. Run the Validator
Use the model just like any Pydantic model. The transforms run **before** validation.

```python
data = {"user": {"name": "alice_wonderland"}}
model = UserProfile(**data)

print(model.display_name)
# Output: "Alice_wond"
```

---

## 📊 Process Flow

The system processes data in a strictly defined pipeline to ensure consistency.

```mermaid
flowchart LR
    raw[Raw JSON Input] --> transform_init[TransformBaseModel Init]
    
    subgraph Transformation Phase
        transform_init --> engine[Step Engine Execution]
        engine --> paths[Execute path() Lookups]
        paths --> steps[Apply Transforms (pipe/nested)]
        steps --> merge[Merge & Override Input Data]
    end
    
    merge --> validation[Pydantic Validation]
    validation --> types[Type Coercion & Checks]
    
    types --> output[Final Validated Model]
    
    style transform_init fill:#f9f,stroke:#333
    style output fill:#9f9,stroke:#333
```

---

## 📂 Project Structure

```text
validator_blackbox/
├── src/
│   ├── main.py              # Entry point runner
│   ├── rules.py             # User-defined Models & Transform definitions
│   ├── function_pool.py     # Registry of allowed Transform functions (User logic goes here)
│   ├── step_engine.py       # Core Engine (Step, Pipe logic)
│   ├── custom_basemodel.py  # Pydantic base integration
│   ├── custom_types.py      # Custom strict types (Passport check, etc.)
│   └── gstin_state_codes_india.json # Reference data
├── tests/
│   ├── test.py              # Primary transformation unit tests
│   └── override_test.py     # Tests for validation logic
├── sample.json              # Complex sample input data
└── requirements.txt         # Dependencies (pydantic, jsonpath-ng)
```

**Key Files:**
- `rules.py`: This is where you work. Define your Pydantic models here.
- `function_pool.py`: Extensions go here. Add new transformation functions (like `REVERSE`, `LOOKUP`, etc.).
- `main.py`: A runner script to demonstrate the system in action.

---

## 🧪 Testing

The project includes a test suite to ensure transformations and validation logic work as expected.

**Run tests:**
```bash
python tests/test.py
```

`tests/test.py` covers:
- **Transform Order**: Ensuring transforms happen before type checks.
- **Missing Fields**: Verifying that required fields are flagged if transforms fail.
- **Type Safety**: Checking that transformed outputs match field types (e.g., `str` to `int`).
- **Defaults**: Ensuring default values are applied when paths are missing.

---

## 🧪 Detailed Sample Input & Output

The following example is available in `src/rules.py` as `TravelSummaryModel`.

**Input (`sample.json` snippet)**
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

**Transformation Logic**
The goal is to create a human-readable summary string from multiple nested fields.
```python
Field(
    transform=join_parts(
        path("$.visa_request_information..from_country_full_name"),
        " → ",
        path("$.visa_request_information..to_country_full_name"),
        " (",
        path("$.visa_request_information..departure_date_formatted"),
        " to ",
        path("$.visa_request_information..arrival_date_formatted"),
        ")"
    )
)
```

**Resulting Output**
```text
India → Taiwan (01-Mar-2026 to 07-Mar-2026)
```

### Nested Transformation Example (Name Composition)

**Input**
```json
{
  "passport": {
      "first_name": "PAULSTALIN JOONIS EVANS",
      "surname": "GODFREY PREM KIRUBA SEKAR"
  }
}
```

**Transformation Logic**
This example uses the `NestedNameModel` to demonstrate the **nested-call syntax**. It extracts the first 10 characters of the first name, capitalizes them, does the same for the first 7 characters of the surname, and joins them.
```python
class NestedNameModel(TransformBaseModel):
    nested_full_name: str = Field(
        transform=join_parts(
            CAPITALIZE(SUBSTR(0, 10, path("$..first_name"))),
            " ",
            CAPITALIZE(SUBSTR(0, 7, path("$..surname"))),
        )
    )
```

**Resulting Output**
```text
Paulstalin Godfrey
```

### GST Output Example

**Input**
```json
{
  "gst_records": [
    { "gst_number": "29ABCDE1234F1Z5" },
    { "gst_number": "27PQRSX5678L1Z3" }
  ]
}
```

**Transformation Logic**
Extracts GST number, derives PAN (chars 3-12), and looks up State Name based on the first 2 digits.
```python
Field(
    transform=path("$.gst_records") | GST_DETAILS_ALL()
)
```

**Resulting Output**
```python
[
  {'gst_number': '29ABCDE1234F1Z5', 'pan_number': 'ABCDE1234F', 'state_name': 'Karnataka'},
  {'gst_number': '27PQRSX5678L1Z3', 'pan_number': 'PQRSX5678L', 'state_name': 'Maharashtra'}
]
```

---

## Important Notes

1. **Precedence**: By default, **Transforms override Input**.
   - If a transform returns a value (not `None`), it replaces the value in the input dictionary.
   - If you want Pydantic defaults to apply, your transform must return `None`.

2. **Extending**: To add new logic (e.g., `REVERSE`), edit `src/function_pool.py`.
   - Always return a `Step`.
   - Use the factory pattern if you want to support both nested and pipe usage (see `CAPITALIZE` implementation).

3. **Performance**: JSONPath lookups are done at runtime. For extremely high-throughput paths, ensure your JSONPaths are specific to avoid full-document scans.

---
