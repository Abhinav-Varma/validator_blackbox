"""
Entry point: load JSON, run through models defined in rules.py, print outputs.
Demonstrates both instantiation styles:
1. Model.model_validate(data)
2. Model(**data)
"""
import json
from src.rules import OutputModel, TravelSummaryModel, GSTAllModel


def main() -> None:
    try:
        with open("sample.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: sample.json not found in the current directory.")
        return
    except json.JSONDecodeError:
        print("Error: sample.json contains invalid JSON.")
        return

    print("=" * 60)
    print("Running models using .model_validate(data)  (recommended Pydantic v2 style)")
    print("=" * 60)

    out1 = OutputModel.model_validate(data)
    print("Output 1 – Full Name :", out1.full_name)

    travel1 = TravelSummaryModel.model_validate(data)
    print("\nOutput 2 – Travel Summary:", travel1.travel_summary)

    gst1 = GSTAllModel.model_validate(data)
    print("\nOutput 3 – All GST outputs:")
    if not gst1.gst_outputs:
        print("  (no GST records found)")
    else:
        for record in gst1.gst_outputs:
            print(" ", record)

    print("\n" + "=" * 60)
    print("Running models using **data unpacking  (classic style)")
    print("=" * 60)

    out2 = OutputModel(data)
    print("Output 1 – Full Name :", out2.full_name)

    travel2 = TravelSummaryModel(**data)
    print("\nOutput 2 – Travel Summary:", travel2.travel_summary)

    gst2 = GSTAllModel(**data)
    print("\nOutput 3 – All GST outputs:")
    if not gst2.gst_outputs:
        print("  (no GST records found)")
    else:
        for record in gst2.gst_outputs:
            print(" ", record)


if __name__ == "__main__":
    main()