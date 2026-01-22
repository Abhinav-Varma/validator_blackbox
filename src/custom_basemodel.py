import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field as PydanticField
from pydantic.fields import FieldInfo
from src.transform import transformer

class TransformFieldInfo(FieldInfo):
    """Enhanced FieldInfo that supports function_logic"""
    def __init__(self, *, function_logic: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.function_logic = function_logic

# Override the Field function to support function_logic
def Field(
    *,
    function_logic: Optional[str] = None,
    **kwargs
) -> FieldInfo:
    """
    Enhanced Field function that supports function_logic for transformations.
    
    Usage:
        field_name: str = Field(
            description="My field",
            function_logic="CAPITALIZE($..field_name)"
        )
    """
    if function_logic is not None:
        return TransformFieldInfo(function_logic=function_logic, **kwargs)
    else:
        return PydanticField(**kwargs)

class TransformBaseModel(BaseModel):
    """Base model that supports automatic transformation using standard Pydantic Field()"""
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None, **data):
        # If json_data is provided, apply transformations
        if json_data is not None:
            # Get all fields with transformation logic
            for field_name, field_info in self.model_fields.items():
                if field_name not in data:
                    # Check if field has transformation logic
                    if isinstance(field_info, TransformFieldInfo) and field_info.function_logic:
                        # Apply transformation
                        data[field_name] = transformer(field_info.function_logic, json_data)
        
        super().__init__(**data)