# JSON Transformation Framework (Python JSLT Equivalent)

## 📋 Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Detailed Architecture](#detailed-architecture)
- [Core Components](#core-components)
- [How It Works](#how-it-works)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [JSONPath Support](#jsonpath-support)
- [Pydantic Integration](#pydantic-integration)
- [Extending the Framework](#extending-the-framework)

## 🎯 Overview

This framework provides:
- **JSON querying** using JSONPath expressions
- **JSON transformation** using custom functions in field
- **Pydantic-based validation** with automatic in field transformation
- **Dynamic data extraction** from JSON files
- BaseModel features are preserved

### 🚀 Quick Start

```python
# 1. Define a model with transformation logic
class CustomerModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(
        function_logic="CONCATENATE(CAPITALIZE($..first_name), '.', CAPITALIZE($..last_name))"
    )

# 2. Load JSON data and create model
with open('data.json') as f:
    json_data = json.load(f)

customer = CustomerModel(json_data=json_data)
print(customer.full_name)  # Output: "John . Doe"
```

## 🔍 Detailed Architecture

### Logical Flow

```
JSON File → JSONPath Extraction → Function Execution → Pydantic Model
     ↓              ↓                    ↓                ↓
  {"first_name":  $..first_name →   CAPITALIZE('john')  →  full_name: "John"
   "last_name":   $..last_name →   CAPITALIZE('doe')    →  "John . Doe"
   "doe"}
```

### Core Components

#### 1. **Function Pool** (`src/function_pool.py`)
- Contains transformation functions (CONCATENATE, CAPITALIZE)
- Extensible - add your own functions here
- Functions are automatically available in transformation context

#### 2. **Transformer Engine** (`src/transform.py`)
- Parses JSONPath expressions from logic strings
- Extracts values from JSON data using jsonpath-ng
- Executes transformation functions with extracted values
- Handles errors gracefully

#### 3. **TransformBaseModel** (`src/custom_basemodel.py`)
- Extends Pydantic's BaseModel
- Provides `TransformField()` for defining transformation logic
- Automatically applies transformations during model creation
- Maintains all BaseModel features (validation, serialization, etc.)

#### 4. **Demonstration** (`src/main.py`)
- Has a smoll demo on the working

## 🏗️ How It Works

### Step 1: JSONPath Parsing
```python
# Logic string: "CONCATENATE(CAPITALIZE($..first_name), '.', CAPITALIZE($..last_name))"
# JSON data: {"first_name": "john", "details": {"last_name": "doe"}}

# The transformer finds JSONPath expressions:
# - $..first_name → "john"
# - $..last_name → "doe"
```

### Step 2: Value Extraction
```python
# Uses jsonpath-ng library to extract values
parser = parse("$..first_name")
matches = parser.find(json_data)
# matches[0].value = "john"
```

### Step 3: Function Execution
```python
# Replaces JSONPath with extracted values:
# "CONCATENATE(CAPITALIZE('john'), CAPITALIZE('doe'))"

# Executes in context with available functions:
exec_context = {"CONCATENATE": CONCATENATE, "CAPITALIZE": CAPITALIZE}
# Result: "John Doe"
```

### Step 4: Model Population
```python
# Transformed value is assigned to model field
customer.full_name = "John Doe"
```

## ✨ Features

### 🔧 JSONPath Support (CHECK)
- Deep querying with `$..field` syntax
- Nested object access
- Array handling
- Fallback to empty string if path not found

### 🛡️ Pydantic Integration (CHECK)
All BaseModel features are preserved

#### Validation
```python
class CustomerModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(
        function_logic="CONCATENATE(CAPITALIZE($..first_name), CAPITALIZE($..last_name))"
    )
    age: int = Field(ge=0, le=150)  # Standard Pydantic validation
    
customer = CustomerModel(json_data=json_data, age=25)
```

#### Field Validators
```python
class CustomerModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(...)
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('Name too short')
        return v
```

#### Computed Fields
```python
class CustomerModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(...)
    
    @computed_field
    @property
    def name_length(self) -> int:
        return len(self.full_name)
```

#### Serialization
```python
customer = CustomerModel(json_data=json_data)
customer.model_dump()  # {'full_name': 'John . Doe'}
customer.model_dump_json()  # '{"full_name": "John . Doe"}'
```

#### Config Options
```python
class CustomerModel(TransformBaseModel):
    class Config:
        validate_assignment = True  # Validate on assignment
        use_enum_values = True      # Use enum values instead of instances
        # ... all standard Pydantic config options
```

## 📖 Usage Examples

### Basic Usage
```python
# Define model
class PersonModel(TransformBaseModel):
    display_name: str = TransformBaseModel.TransformField(
        function_logic="CONCATENATE(CAPITALIZE($..first_name), CAPITALIZE($..last_name))"
    )

# Use model
person = PersonModel(json_data={"first_name": "alice", "last_name": "smith"})
print(person.display_name)  # "Alice Smith"
```

### Multiple Fields
```python
class CustomerModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(
        function_logic="CONCATENATE(CAPITALIZE($..first_name), CAPITALIZE($..last_name))"
    )
    email_domain: str = TransformBaseModel.TransformField(
        function_logic="CAPITALIZE($..email)"
    )
    is_premium: bool = Field(default=False)
```

### With Validators (WHY?)
```python
class ValidatedModel(TransformBaseModel):
    transformed_field: str = TransformBaseModel.TransformField(...)
    normal_field: str
    
    @field_validator('transformed_field', 'normal_field')
    @classmethod
    def validate_fields(cls, v: str) -> str:
        return v.strip()
```

## 🔧 Extending the Framework

### Adding New Functions
```python
# src/function_pool.py
def UPPERCASE(text: str) -> str:
    return text.upper()

def REVERSE(text: str) -> str:
    return text[::-1]

# src/transform.py
FUNCTIONS = {
    "CONCATENATE": CONCATENATE,
    "CAPITALIZE": CAPITALIZE,
    "UPPERCASE": UPPERCASE,
    "REVERSE": REVERSE,
}
```

### Custom TransformBaseModel (Extending the framework... is this required??)
```python
class CustomTransformModel(TransformBaseModel):
    class Config:
        # Custom configuration
        validate_all = True
        use_enum_values = True
    
    @staticmethod
    def CustomTransformField(function_logic: Optional[str] = None, **kwargs):
        """Custom field factory with additional options"""
        return TransformFieldInfo(function_logic=function_logic, **kwargs)
```

## 🧪 Testing (This is wrong #needfix + Further parts need fix as well)

```python
# Test with different JSON structures
test_cases = [
    {"first_name": "john", "last_name": "doe"},
    {"user": {"first_name": "jane", "last_name": "smith"}},
    {"data": {"person": {"first_name": "bob", "last_name": "johnson"}}},
]

for test_data in test_cases:
    model = CustomerModel(json_data=test_data)
    print(f"Result: {model.full_name}")
```

## 📊 Performance Considerations

- JSONPath expressions are cached during transformation
- Functions are executed in a pre-built context for efficiency
- Pydantic's validation is only run once after transformation
- Large JSON files are processed incrementally where possible

## 🎯 Summary

This framework provides a powerful, extensible way to:
1. **Query JSON data** using JSONPath expressions
2. **Transform data** using custom functions
3. **Validate results** using Pydantic's robust validation system
4. **Maintain type safety** throughout the process
5. **Extend functionality** by adding new functions and validators

The key innovation is the seamless integration of JSONPath querying, functional transformation, and Pydantic validation in a single, cohesive framework that maintains all the benefits of standard Pydantic models.
