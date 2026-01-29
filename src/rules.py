"""
All user-defined transformation models.
New models are added here; they are instantly usable in main.py.
"""
from typing import List, Dict, Literal

from typing_extensions import Annotated
from pydantic.types import StringConstraints
from src.custom_basemodel import TransformBaseModel, Field
from src.step_engine import path
from src.function_pool import (  # whitelist only what you need
    CAPITALIZE,
    join_parts,
    GST_DETAILS_ALL,
    SUBSTR,
)

# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
class NameModel(TransformBaseModel):
    full_name: Annotated[
        str,
        #StringConstraints(max_length=10)
        StringConstraints(min_length=10)
    ] = Field(
        description="Full name of the customer",
        transform=join_parts(
            path("$..first_name") | SUBSTR(0,10) | CAPITALIZE(),
            " ",
            path("$..surname") | CAPITALIZE() | SUBSTR(0,7),
        ),
    )


class NestedNameModel(TransformBaseModel):
    nested_full_name: str = Field(
        description="Full name using nested function-call style",
        transform=join_parts(
            CAPITALIZE(SUBSTR(0, 10, path("$..first_name"))),
            " ",
            CAPITALIZE(SUBSTR(0, 7, path("$..surname"))),
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


class DefaultPreservationModel(TransformBaseModel):
    country: str = Field(
        default="Unknown",
        transform=path("$.country"),  # returns None if missing
    )


# ---- custom types ----
from src.custom_types import (
    NonEmptyStr,
    PassportNumber,
)

class CustomerVisaProfileModel(TransformBaseModel):
    full_name: NonEmptyStr = Field(
        description="Customer full name",
        transform=join_parts(
            path("$..first_name") | CAPITALIZE(),
            " ",
            path("$..surname") | CAPITALIZE(),
        ),
    )

    gender: Literal["M", "F", "O"] = Field(
        transform=path("$..gender"),
    )

    passport_number: PassportNumber = Field(
        transform=path("$..passport_number") | SUBSTR(0, 9),
    )
    gst_outputs: List[Dict[str, str]] = Field(
        default=[],
        transform=path("$..gst_records") | GST_DETAILS_ALL(),
    )

