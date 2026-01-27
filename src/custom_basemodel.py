# src/custom_basemodel.py
from pydantic import Field as PydanticField, BaseModel, model_validator
from typing import Any, Callable, Dict
from src.step_engine import Step

def Field(
    *,
    default: Any = ...,
    transform: Callable[[Step], Step] | None = None,
    **kwargs,
):
    return PydanticField(
        default=default,
        json_schema_extra={
            "transform": transform,
        },
        **kwargs,
    )

class TransformBaseModel(BaseModel):
    """
    BaseModel that applies field-level transforms BEFORE validation.
    """

    @model_validator(mode="before")
    @classmethod
    def _apply_transforms(cls, input_data: Any):
        """
        input_data is raw:
        - dict
        - JSON-decoded object
        - positional dict (Model(data))
        """

        # Handle positional dict case: Model(data)
        if not isinstance(input_data, dict):
            return input_data

        data = dict(input_data)  # shallow copy (important)

        for field_name, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra or {}
            transform = extra.get("transform")

            if transform is None:
                continue

            try:
                value = transform(input_data)
            except Exception as e:
                raise ValueError(
                    f"Transform failed for field '{field_name}': {e}"
                ) from e

            data[field_name] = value

        return data

    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }
