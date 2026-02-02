"""
All user-defined transformation models.
"""
from typing import List, Dict, Literal
from typing_extensions import Annotated
from pydantic.types import StringConstraints

from src.custom_basemodel import TransformBaseModel, Field
from src.step_engine import path
from src.function_pool import CAPITALIZE, SUBSTR, join_parts, GST_DETAILS_ALL
from src.custom_types import NonEmptyStr, PassportNumber


class CustomerNameModel(TransformBaseModel):
    """Model demonstrating pipeline and nested function-call style transforms"""
    # Pipeline style: path | SUBSTR | CAPITALIZE
    full_name: Annotated[
        str,
        StringConstraints(min_length=10)
    ] = Field(
        description="Full name using pipeline style transforms",
        transform=join_parts(
            path("$..first_name") | SUBSTR(0,10) | CAPITALIZE(),
            " ",
            path("$..surname") | CAPITALIZE() | SUBSTR(0,7),
        ),
    )

    # Nested function-call style: CAPITALIZE(SUBSTR(path))
    display_name: str = Field(
        description="Display name using nested function-call style",
        transform=join_parts(
            CAPITALIZE(SUBSTR(0, 10, path("$..first_name"))),
            " ",
            CAPITALIZE(SUBSTR(0, 7, path("$..surname"))),
        ),
    )


class TravelInfoModel(TransformBaseModel):
    """Model demonstrating complex path extraction and custom types"""
    # Complex nested path extraction
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

    # Default value demonstration
    country: str = Field(
        default="Unknown",
        transform=path("$.country"),
    )


class CustomerProfileModel(TransformBaseModel):
    """Model demonstrating custom types and list processing"""
    # Custom type with validation (PassportNumber)
    passport_number: PassportNumber = Field(
        transform=path("$..passport_number") | SUBSTR(0, 9),
    )

    # Literal type validation
    gender: Literal["M", "F", "O"] = Field(
        transform=path("$..gender"),
    )

    # NonEmptyStr custom type
    customer_name: NonEmptyStr = Field(
        description="Customer name using NonEmptyStr type",
        transform=join_parts(
            path("$..first_name") | CAPITALIZE(),
            " ",
            path("$..surname") | CAPITALIZE(),
        ),
    )

    # GST list processing with default
    gst_outputs: List[Dict[str, str]] = Field(
        default=[],
        transform=path("$.gst_records") | GST_DETAILS_ALL(),
    )
