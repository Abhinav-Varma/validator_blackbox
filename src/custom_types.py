# custom_types.py
from pydantic_core import core_schema


class NonEmptyStr(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("must be a non-empty string")
        return cls(value)


class PassportNumber(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(min_length=6, max_length=9),
        )

    @classmethod
    def _validate(cls, value: str):
        if not value.isalnum():
            raise ValueError("passport number must be alphanumeric")
        return cls(value.upper())
