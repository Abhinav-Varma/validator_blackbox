# src/custom_basemodel.py
from pydantic import Field as PydanticField, BaseModel, model_validator
from typing import Any, Callable, Dict
from src.expression_constructor import ExpressionConstructor


def Field(
    *,
    default: Any = ...,
    transform: Dict[str, Any] | None = None,
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
    BaseModel that applies field-level transforms BEFORE validation using JSONLogic.
    """

    @model_validator(mode="before")
    @classmethod
    def _apply_transforms(cls, input_data: Any):
        if not isinstance(input_data, dict):
            return input_data

        data = dict(input_data)

        for field_name, field_info in cls.model_fields.items():
            # Attempt to run a transform if one is defined
            extra = field_info.json_schema_extra or {}
            transform = extra.get("transform")
            if transform is None:
                continue

            # Convert nested expression to JSONLogic rule
            jsonlogic_rule = ExpressionConstructor.construct(transform)
            
            # Apply JSONLogic rule to extract and transform data
            value = ExpressionConstructor.apply(jsonlogic_rule, input_data)
            if value is not None:
                data[field_name] = value

        return data

    # dumping extras for security
    @model_validator(mode="after")
    def _strip_extras(self):
        """
        Permanently remove extra input data after validation.
        This enforces output isolation.
        """
        if hasattr(self, "__pydantic_extra__"):
            self.__pydantic_extra__.clear()
        return self

    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }
