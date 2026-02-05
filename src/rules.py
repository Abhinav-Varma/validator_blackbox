"""
All user-defined transformation models.
New models are added here; they are instantly usable in main.py.
"""

from typing import List, Dict

from src.custom_basemodel import TransformBaseModel, Field
from src.step_engine import path
from src.function_pool import CAPITALIZE, SUBSTR, join_parts, GST_DETAILS_ALL, JSONLOGIC
from src.custom_types import NonEmptyStr, PassportNumber

# ------------------------------------------------------------------
# Core Models
# ------------------------------------------------------------------

class CustomerNameModel(TransformBaseModel):
    full_name: NonEmptyStr = Field(
        description="Customer full name",
        transform=join_parts(
            CAPITALIZE(SUBSTR(0, 10, path("$..first_name"))),
            " ",
            CAPITALIZE(SUBSTR(0, 7, path("$..surname"))),
        ),
    )


class TravelInfoModel(TransformBaseModel):
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


class CustomerProfileModel(TransformBaseModel):
    passport_number: PassportNumber = Field(
        transform=SUBSTR(0, 9, path("$..passport_number")),
    )

    gst_outputs: List[Dict[str, str]] = Field(
        default=[],
        transform=path("$..gst_records") | GST_DETAILS_ALL(),
    )


# ------------------------------------------------------------------
# JsonLogic-backed models
# ------------------------------------------------------------------

class DocumentSummaryModel(TransformBaseModel):
    """Collects key document filenames from the payload for quick inspection."""

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
    """Consolidated location information."""

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
        transform=CAPITALIZE(
            JSONLOGIC({
                "if": [
                    {"missing": ["residential_address.residential_address_card_v2.city"]},
                    {"var": "passport.passport_details.place_of_issue"},
                    {"cat": [
                        {"var": "residential_address.residential_address_card_v2.city"},
                        ", ",
                        {"var": "residential_address.residential_address_card_v2.state"}
                    ]}
                ]
            })
        ),
    )

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
        }),
    )
