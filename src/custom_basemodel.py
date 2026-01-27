from typing import Any, Dict, Optional, Callable

from pydantic import BaseModel, model_validator, ValidationError
from pydantic.fields import FieldInfo as PydanticFieldInfo

from src.step_engine import Step


class TransformFieldInfo(PydanticFieldInfo):
    transform: Optional[Step[Any, Any]] = None
    post_transform: Optional[Callable[[Any], Any]] = None  # optional hook

    def __init__(
        self,
        *,
        transform: Optional[Step[Any, Any]] = None,
        post_transform: Optional[Callable[[Any], Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.transform = transform
        self.post_transform = post_transform


def Field(
    *,
    transform: Optional[Step[Any, Any]] = None,
    post_transform: Optional[Callable[[Any], Any]] = None,
    **kwargs: Any,
) -> PydanticFieldInfo:
    if transform is not None or post_transform is not None:
        return TransformFieldInfo(transform=transform, post_transform=post_transform, **kwargs)
    return PydanticFieldInfo(**kwargs)


class TransformBaseModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def _apply_transforms(cls, data: Any) -> Dict[str, Any]:
        if not isinstance(data, dict):
            return data

        transformed = data.copy()

        for field_name, field_info in cls.model_fields.items():
            transform_step = getattr(field_info, 'transform', None)
            post_fn = getattr(field_info, 'post_transform', None)

            if transform_step is not None:
                try:
                    value = transform_step(data)

                    # Apply optional post-processing (user-defined)
                    if post_fn is not None:
                        value = post_fn(value)

                    # Only assign if we got a meaningful value
                    # → if None / empty / falsy → leave field missing → default applies
                    if value is not None and value != "" and (not isinstance(value, (list, dict)) or value):
                        transformed[field_name] = value

                    # If you want stricter control, you can raise here for required fields:
                    # elif field_info.is_required():
                    #     raise ValueError(f"Required field '{field_name}' got no value from transform")

                except Exception as exc:
                    raise ValidationError.from_exception_data(
                        title=f"Transformation failed for {field_name}",
                        errors=[{'type': 'value_error', 'loc': (field_name,), 'msg': str(exc)}]
                    ) from exc

        return transformed