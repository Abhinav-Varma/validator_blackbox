"""
All user-defined transformation models.
New models are added here; they are instantly usable in main.py.
"""
from typing import List, Dict
from src.custom_basemodel import TransformBaseModel, Field
from src.step_engine import path
<<<<<<< Updated upstream
from src.function_pool import (  # whitelist only what you need
    CAPITALIZE,
    join_parts,
    GST_DETAILS_ALL,
    SUBSTR,
)
=======
from src.function_pool import CAPITALIZE, SUBSTR, join_parts, GST_DETAILS_ALL
from src.custom_types import NonEmptyStr, PassportNumber
from src.function_pool import JSONLOGIC
>>>>>>> Stashed changes

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
# JsonLogic-backed customer models removed as requested.


class DocumentSummaryModel(TransformBaseModel):
    """Collects key document filenames from the payload for quick inspection."""
    # Classic jsonlogic usage: `var` to extract values and `and` to test presence
    passport_front: str | None = Field(
        default=None,
        transform=JSONLOGIC({"var": "passport.passport_details.ovd_front.doc_name"}),
    )

    passport_back: str | None = Field(
        default=None,
        transform=JSONLOGIC({"var": "passport.passport_details.ovd_back.doc_name"}),
    )

    instruction_doc: str | None = Field(
        default=None,
        transform=JSONLOGIC({"var": "consultant_info.instruction_letter.upload_instruction.doc_name"}),
    )

    application_form_doc: str | None = Field(
        default=None,
        transform=JSONLOGIC({"var": "consultant_info.application_form.application_form.doc_name"}),
    )

    # boolean showing both passport front and back are present
    has_passport_docs: bool = Field(
        default=False,
        transform=JSONLOGIC({
            "and": [
                {"!=": [{"var": "passport.passport_details.ovd_front.doc_name"}, None]},
                {"!=": [{"var": "passport.passport_details.ovd_back.doc_name"}, None]}
            ]
        }),
    )


class LocationModel(TransformBaseModel):
    """Consolidated location information (residential vs passport place of issue).

    Uses JsonLogic to prefer residential address when available, otherwise falls
    back to passport place of issue.
    """
    residential: str = Field(
        transform=join_parts(
            path("$.residential_address.residential_address_card_v2.city"),
            ", ",
            path("$.residential_address.residential_address_card_v2.state"),
            " ",
            path("$.residential_address.residential_address_card_v2.pin_code"),
        )
    )

    passport_place_of_issue: str = Field(
        transform=path("$.passport.passport_details.place_of_issue"),
    )

    preferred_location: str = Field(
        description="Residential location when present, else passport place of issue",
        transform=JSONLOGIC({
            # if residential city is missing -> use passport place, else build residential string
            "if": [
                {"missing": ["residential_address.residential_address_card_v2.city"]},
                {"var": "passport.passport_details.place_of_issue"},
                {"cat": [
                    {"var": "residential_address.residential_address_card_v2.city"},
                    ", ",
                    {"var": "residential_address.residential_address_card_v2.state"}
                ]}
            ]
        }) | CAPITALIZE()
    )

    # Demonstrate classic comparisons and branching
    nearby_state_match: bool = Field(
        default=False,
        transform=JSONLOGIC({
            "==": [
                {"var": "passport.passport_details.place_of_issue"},
                {"var": "residential_address.residential_address_card_v2.state"}
            ]
        }),
    )

    age_group: str = Field(
        transform=JSONLOGIC({
            "if": [
                {"<": [{"var": "passport.passport_details.age"}, 18]},
                "Minor",
                {"<": [{"var": "passport.passport_details.age"}, 60]},
                "Adult",
                "Senior"
            ]
        })
    )
    
