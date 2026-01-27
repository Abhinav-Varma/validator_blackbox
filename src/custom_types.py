# custom_types.py
from pydantic_core import core_schema
import re

# Class to validate non-empty strings
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

# Class to validate email addresses
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class EmailAddress(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: str):
        if not _EMAIL_RE.match(value):
            raise ValueError("invalid email address")
        return cls(value.lower())

# Class to validate passport numbers
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
