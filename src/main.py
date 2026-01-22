import json
from typing import List, Dict
from src.custom_basemodel import TransformBaseModel
from src.toolkit import Path, call
from src.function_pool import (
    CONCATENATE,
    CAPITALIZE,
    JOIN,
    GST_DETAILS_ALL,
)

class OutputModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(
        logic=call(
            CONCATENATE,
            call(CAPITALIZE, Path("$..first_name")),
            call(CAPITALIZE, Path("$..surname")),
        )
    )


class TravelSummaryModel(TransformBaseModel):
    travel_summary: str = TransformBaseModel.TransformField(
        logic=call(
            JOIN,
            Path("$..visa_request_information.visa_request.from_country_full_name"),
            " → ",
            Path("$..visa_request_information.visa_request.to_country_full_name"),
            " (",
            Path("$..visa_request_information.visa_request.departure_date_formatted"),
            " to ",
            Path("$..visa_request_information.visa_request.arrival_date_formatted"),
            ")",
        )
    )


class GSTAllModel(TransformBaseModel):
    gst_outputs: List[Dict[str, str]] = TransformBaseModel.TransformField(
        logic=call(
            GST_DETAILS_ALL,
            Path("$..gst_records"),
        )
    )


if __name__ == "__main__":
    with open("sample.json", "r") as f:
        json_data = json.load(f)
    print("\nOutput 1:\n")
    print(OutputModel(json_data=json_data).full_name)
    print("\nOutput 2:\n")
    print(TravelSummaryModel(json_data=json_data).travel_summary)
    print("\nOutput 3:\n")
    for r in GSTAllModel(json_data=json_data).gst_outputs:
        print(r)
