import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from src.transform import transformer

class TransformFieldInfo(FieldInfo):
    """Custom FieldInfo that includes transformation logic"""
    def __init__(self, function_logic: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.function_logic = function_logic

class TransformBaseModel(BaseModel):
    """Base model that supports automatic transformation"""
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None, **data):
        # If json_data is provided, apply transformations
        if json_data is not None:
            # Get all fields with transformation logic
            for field_name, field_info in self.model_fields.items():
                if (isinstance(field_info, TransformFieldInfo) and 
                    field_info.function_logic and 
                    field_name not in data):
                    # Apply transformation
                    data[field_name] = transformer(field_info.function_logic, json_data)
        
        super().__init__(**data)
    
    @staticmethod
    def TransformField(function_logic: Optional[str] = None, **kwargs):
        """Factory function for creating transformation fields - included in TransformBaseModel"""
        return TransformFieldInfo(function_logic=function_logic, **kwargs)
