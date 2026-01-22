"""
Pydantic base model that understands Step-based transforms.
Importing this module makes `transform=` auto-complete appear in rules.py.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field as PydanticField
from pydantic.fields import FieldInfo
from src.step_engine import Step  # re-exported for convenience

# ------------------------------------------------------------------
# Field descriptor
# ------------------------------------------------------------------
class TransformFieldInfo(FieldInfo):
    def __init__(self, *, transform: Step[Any, Any] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.transform = transform

def Field(*, transform: Step[Any, Any] | None = None, **kwargs) -> FieldInfo:
    return TransformFieldInfo(transform=transform, **kwargs) if transform else PydanticField(**kwargs)

# ------------------------------------------------------------------
# Base model
# ------------------------------------------------------------------
class TransformBaseModel(BaseModel):
    def __init__(self, json_data: Optional[Dict[str, Any]] = None, **data):
        if json_data is not None:
            for name, field in self.model_fields.items():
                if name not in data and isinstance(field, TransformFieldInfo) and field.transform:
                    data[name] = field.transform(json_data)
        super().__init__(**data)
        #print("DEBUG", name, "transform result", repr(data[name]), type(data[name]))