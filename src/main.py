"""
Entry point: load JSON, run through models defined in rules.py, print outputs.
Demonstrates both instantiation styles:
1. Model.model_validate(data)
2. Model(**data)
"""
import json
from src.rules import NameModel, NestedNameModel, TravelSummaryModel, GSTAllModel, DefaultPreservationModel, CustomerVisaProfileModel


def main() -> None:

    with open("sample.json", "r") as f:
        data = json.load(f)

    out = NameModel(**data)
    print("Output 1 – Full Name :", out.full_name)

    nested = NestedNameModel(**data)
    print("Output 1.n – Nested Full Name:", nested.nested_full_name)

    out = NameModel.model_validate(
        {
            **data,
            "full_name": "MANUAL OVERRIDE",
        }
    )
    print("Output 1.1 – Full Name (Override check):", out.full_name)

    travel = TravelSummaryModel(**data)
    #print("\nOutput 2 – Travel Summary:", travel.travel_summary)

    gst = GSTAllModel.model_validate(data)
    print("\nOutput 3 – All GST outputs:")
    if not gst.gst_outputs:
        print("  (no GST records found)")
    else:
        for record in gst.gst_outputs:
            print(" ", record)

    m = DefaultPreservationModel.model_validate(data)
    #print("Country (Default Check):", m.country)

        
    # --- every normal Pydantic call works ---------------------------------
    m2 = NameModel.model_validate(data)           # explicit validator
    m3 = NameModel.model_validate_json(open("sample.json").read())  # string JSON
    m4 = NameModel.model_validate(data, strict=True)  # strict mode
    m5 = NameModel(**data)                        # kwargs expansion
    # ----------------------------------------------------------------------

    extensivetest = CustomerVisaProfileModel(**data)
    print(extensivetest.model_dump())
    
if __name__ == "__main__":
    main()