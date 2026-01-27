"""
All user-defined transformation models.
New models are added here; they are instantly usable in main.py.
"""
from typing import List, Dict
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
