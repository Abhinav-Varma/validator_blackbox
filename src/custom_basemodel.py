from typing import Any, Dict, Optional
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from src.evaluator import evaluate


class TransformFieldInfo(FieldInfo):
    def __init__(self, logic=None, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic


class TransformBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, json_data: Optional[Dict[str, Any]] = None, **data):
        if json_data:
            for name, field in self.model_fields.items():
                if isinstance(field, TransformFieldInfo) and name not in data:
                    data[name] = evaluate(field.logic, json_data)
        super().__init__(**data)

    @staticmethod
    def TransformField(*, logic, **kwargs):
        return TransformFieldInfo(logic=logic, **kwargs)
