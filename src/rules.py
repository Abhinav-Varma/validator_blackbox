from typing import List, Dict, Optional
from pydantic import ValidationError

from src.custom_basemodel import TransformBaseModel, Field
from src.step_engine import path
from src.function_pool import CAPITALIZE, join_parts, GST_DETAILS_ALL, SUBSTR


# ────────────────────────────────────────────────
# Your production models (unchanged)
# ────────────────────────────────────────────────
class OutputModel(TransformBaseModel):
    full_name: str = Field(
        description="Full name of the customer",
        transform=join_parts(
            path("$..first_name") | SUBSTR(0,10) | CAPITALIZE(),
            " ",
            path("$..surname") | CAPITALIZE() | SUBSTR(0,7),
        ),
    )


class TravelSummaryModel(TransformBaseModel):
    travel_summary: str = Field(
        description="Human readable travel summary",
        transform=join_parts(
            path("$.visa_request_information.visa_request.from_country_full_name"),
            " → ",
            path("$.visa_request_information.visa_request.to_country_full_name"),
            " (",
            path("$.visa_request_information.visa_request.departure_date_formatted"),
            " to ",
            path("$.visa_request_information.visa_request.arrival_date_formatted"),
            ")",
        ),
    )


class GSTAllModel(TransformBaseModel):
    gst_outputs: List[Dict[str, str]] = Field(
        description="GST details for ALL GST numbers",
        transform=path("$.gst_records") | GST_DETAILS_ALL(),
    )


# ────────────────────────────────────────────────
# Test model to verify transform order (add this)
# ────────────────────────────────────────────────
class TransformOrderTestModel(TransformBaseModel):
    """
    Use this model to confirm that transformations run BEFORE Pydantic field validation.
    Run the test function below to see the behaviour.
    """
    name: str = Field(
        description="Uppercase sliced name from user.first + user.last",
        transform=join_parts(
            path("$.user.first") | SUBSTR(0, 5) | CAPITALIZE(),
            " ",
            path("$.user.last") | CAPITALIZE(),
        ),
    )

    age: int = Field(  # Note: PositiveInt would be stricter, but int for simplicity
        description="Must be integer after transform (coerces string → int)",
        transform=path("$.user.age"),
    )

    country: str = Field(
        default="Unknown",
        description="Should override default if present in input",
        transform=path("$.user.country"),
    )

    nickname: Optional[str] = Field(
        default=None,
        transform=path("$.user.nickname"),
    )


def test_transform_order():
    """Run this to verify transform → validation order"""
    print("=== Testing transform order ===\n")

    # Case 1: Complete good data
    good = {
        "user": {
            "first": "alexander",
            "last": "hamilton",
            "age": "42",           # string → coerced to int
            "country": "USA",
            "nickname": "Alex"
        }
    }
    print("Case 1 - Good data:")
    try:
        m = TransformOrderTestModel.model_validate(good)
        print("Success →", m.model_dump())
    except ValidationError as e:
        print("Failed:", e.errors(include_url=False))
    print()

    # Case 2: Missing required field (age)
    missing_age = {
        "user": {
            "first": "maria",
            "last": "sousa",
            "country": "Brazil"
        }
    }
    print("Case 2 - Missing required field 'age':")
    try:
        m = TransformOrderTestModel.model_validate(missing_age)
        print("Unexpected success →", m.model_dump())
    except ValidationError as e:
        print("Correctly failed:", e.errors(include_url=False))
    print()

    # Case 3: Wrong type that can't be coerced
    bad_type = {
        "user": {
            "first": "julia",
            "last": "roberts",
            "age": "thirty",      # can't become int
            "country": "Canada"
        }
    }
    print("Case 3 - Invalid type for age:")
    try:
        m = TransformOrderTestModel.model_validate(bad_type)
        print("Unexpected success →", m.model_dump())
    except ValidationError as e:
        print("Correctly failed:", e.errors(include_url=False))
    print()

    # Case 4: Missing optional/default field
    no_country = {
        "user": {
            "first": "carlos",
            "last": "slim",
            "age": 55,
        }
    }
    print("Case 4 - No country (default should apply):")
    m = TransformOrderTestModel.model_validate(no_country)
    print("Result → country =", m.country)


# Run the test when file is executed directly
if __name__ == "__main__":
    test_transform_order()