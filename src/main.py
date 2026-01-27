"""
Entry point: load JSON, run through models defined in rules.py, print outputs.
Demonstrates both instantiation styles:
1. Model.model_validate(data)
2. Model(**data)
"""
import json
from src.rules import OutputModel, TravelSummaryModel, GSTAllModel


def main() -> None:

    with open("sample.json", "r") as f:
        data = json.load(f)

    gst1 = GSTAllModel.model_validate(data)
    print("\nOutput 3 – All GST outputs:")
    if not gst1.gst_outputs:
        print("  (no GST records found)")
    else:
        for record in gst1.gst_outputs:
            print(" ", record)

    out2 = OutputModel(**data)
    print("Output 1 – Full Name :", out2.full_name)

    travel2 = TravelSummaryModel(**data)
    print("\nOutput 2 – Travel Summary:", travel2.travel_summary)

if __name__ == "__main__":
    main()