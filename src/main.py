import json
from typing import List, Dict
from src.custom_basemodel import TransformBaseModel, Field

class OutputModel(TransformBaseModel):
    full_name: str = Field(
        description="Full name of the customer",
        function_logic="CONCATENATE(CAPITALIZE($..first_name), CAPITALIZE($..surname))"
    )

class TravelSummaryModel(TransformBaseModel):
    travel_summary: str = Field(
        description="Human readable travel summary",
        function_logic=(
            "JOIN("
            "$..visa_request_information.visa_request.from_country_full_name, "
            "' → ', "
            "$..visa_request_information.visa_request.to_country_full_name, "
            "' (', "
            "$..visa_request_information.visa_request.departure_date_formatted, "
            "' to ', "
            "$..visa_request_information.visa_request.arrival_date_formatted, "
            "')'"
            ")"
        )
    )

class GSTAllModel(TransformBaseModel):
    gst_outputs: List[Dict[str, str]] = Field(
        description="GST details for ALL GST numbers",
        function_logic="GST_DETAILS_ALL($..gst_records)"
    )

if __name__ == "__main__":
    with open("sample.json", "r") as f:
        json_data = json.load(f)

    output = OutputModel(json_data=json_data)
    print("Output 1")
    print("\nFinal Full Name:", output.full_name)

    travel = TravelSummaryModel(json_data=json_data)
    print("\nOutput 2")
    print("\nTravel Summary:", travel.travel_summary)

    gst_all = GSTAllModel(json_data=json_data)
    print("\nOutput 3")
    print("\nAll GST Outputs:")
    for r in gst_all.gst_outputs:
        print(r)
