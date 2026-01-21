# src/main.py
import json
from typing import List, Dict
from src.custom_basemodel import TransformBaseModel

# Define the output model using custom base model
class OutputModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(
        description="Full name of the customer",
        function_logic="CONCATENATE(CAPITALIZE($..first_name), CAPITALIZE($..surname))"
    )

class TravelSummaryModel(TransformBaseModel):
    travel_summary: str = TransformBaseModel.TransformField(
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

class RequestedGSTModel(TransformBaseModel):
    gst_outputs: List[Dict[str, str]] = TransformBaseModel.TransformField(
        description="GST details only for requested GST numbers",
        function_logic="GST_DETAILS_FOR($..requested_gst_numbers, $..gst_records)"
    )


# Example usage
if __name__ == "__main__":
    # Load JSON data from file
    with open('sample.json', 'r') as f:
        json_data = json.load(f)
    
    # Create model instance with automatic transformation
    output = OutputModel(json_data=json_data)
    print("Final Full Name:", output.full_name)  # Expected Output: "John . Doe"

    travel = TravelSummaryModel(json_data=json_data)
    print("\nTravel Summary:", travel.travel_summary)

    # Load base JSON (sample2.json)
    with open("sample2.json", "r") as f:
        base_json = json.load(f)

    # Specify which GSTs you want (runtime selection)
    requested_gsts = [
        "29ABCDE1234F1Z5",
        "07LMNOP9876Q1Z9",
        "18GGGGG7777G1Z7"
    ]

    # Create a derived JSON for GST processing ONLY
    gst_json = {
        **base_json,
        "requested_gst_numbers": requested_gsts
    }

    gst = RequestedGSTModel(json_data=gst_json)

    print("\nRequested GST Outputs:")
    for r in gst.gst_outputs:
        print(r)
