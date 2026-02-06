"""
All user-defined transformation models.
Converted to nested JSONLogic format.
"""
from typing import List, Dict, Literal
from typing_extensions import Annotated
from pydantic.types import StringConstraints

from src.custom_basemodel import TransformBaseModel, Field
from src.expression_constructor import JSONPATH, CAPITALIZE, SUBSTR, JOIN_PARTS, GST_DETAILS_ALL
from src.custom_types import NonEmptyStr, PassportNumber


class CustomerNameModel(TransformBaseModel):
    """Model demonstrating nested function-call style transforms"""
    # Nested function-call style using JSONLogic operators
    full_name: Annotated[
        str,
        StringConstraints(min_length=10)
    ] = Field(
        description="Full name using nested JSONLogic style transforms",
        transform=JOIN_PARTS(
            CAPITALIZE(JSONPATH("$..first_name")),
            " ",
            CAPITALIZE(JSONPATH("$..surname")),
        ),
    )

    # Nested function-call style: CAPITALIZE(SUBSTR(path))
    display_name: str = Field(
        description="Display name using nested function-call style",
        transform=JOIN_PARTS(
            CAPITALIZE(SUBSTR(0, 10, JSONPATH("$..first_name"))),
            " ",
            CAPITALIZE(SUBSTR(0, 7, JSONPATH("$..surname"))),
        ),
    )


class TravelInfoModel(TransformBaseModel):
    """Model demonstrating complex path extraction and custom types"""
    # Complex nested path extraction
    travel_summary: str = Field(
        description="Human readable travel summary",
        transform=JOIN_PARTS(
            JSONPATH("$.visa_request_information.visa_request.from_country_full_name"),
            " → ",
            JSONPATH("$.visa_request_information.visa_request.to_country_full_name"),
            " (",
            JSONPATH("$.visa_request_information.visa_request.departure_date_formatted"),
            " to ",
            JSONPATH("$.visa_request_information.visa_request.arrival_date_formatted"),
            ")",
        ),
    )

    # Default value demonstration
    country: str = Field(
        default="Unknown",
        transform=JSONPATH("$.country"),
    )


class CustomerProfileModel(TransformBaseModel):
    """Model demonstrating custom types and list processing"""
    # Custom type with validation (PassportNumber)
    passport_number: PassportNumber = Field(
        transform=SUBSTR(0, 9, JSONPATH("$..passport_number")),
    )

    # Literal type validation
    gender: Literal["M", "F", "O"] = Field(
        transform=JSONPATH("$..gender"),
    )

    # NonEmptyStr custom type
    customer_name: NonEmptyStr = Field(
        description="Customer name using NonEmptyStr type",
        transform=JOIN_PARTS(
            CAPITALIZE(JSONPATH("$..first_name")),
            " ",
            CAPITALIZE(JSONPATH("$..surname")),
        ),
    )

    # GST list processing with default
    gst_outputs: List[Dict[str, str]] = Field(
        default=[],
        transform=GST_DETAILS_ALL(JSONPATH("$.gst_records")),
    )
