"""
Entry point: load JSON, run through models defined in rules.py, print outputs.
"""
import json
from src.rules import OutputModel, TravelSummaryModel, GSTAllModel

def main() -> None:
    with open("sample.json", "r") as f:
        data = json.load(f)

    out = OutputModel(json_data=data)
    print("Output 1\nFull Name :", out.full_name)

    travel = TravelSummaryModel(json_data=data)
    print("\nOutput 2\nTravel Summary:", travel.travel_summary)

    gst = GSTAllModel(json_data=data)
    print("\nOutput 3\nAll GST outputs:")
    for r in gst.gst_outputs:
        print(r)

if __name__ == "__main__":
    main()