"""
Entry point: load JSON, run through models defined in rules.py, print outputs.
"""
import json
<<<<<<< Updated upstream
from src.rules import OutputModel, TravelSummaryModel, GSTAllModel
=======
from src.rules import (
    CustomerNameModel,
    TravelInfoModel,
    CustomerProfileModel,
    DocumentSummaryModel,
    LocationModel,
)

>>>>>>> Stashed changes

def main() -> None:
    with open("sample.json", "r") as f:
        data = json.load(f)

<<<<<<< Updated upstream
    out = OutputModel(json_data=data)
    print("Output 1\nFull Name :", out.full_name)

    travel = TravelSummaryModel(json_data=data)
    print("\nOutput 2\nTravel Summary:", travel.travel_summary)

    gst = GSTAllModel(json_data=data)
    print("\nOutput 3\nAll GST outputs:")
    for r in gst.gst_outputs:
        print(r)
=======
    # Original model demos
    # CustomerNameModel - pipeline and nested function-call styles
    name_model = CustomerNameModel(**data)
    print("CustomerNameModel Output:")
    print(name_model.model_dump_json(indent=2))
    print()

    # TravelInfoModel - complex paths and defaults
    travel_model = TravelInfoModel(**data)
    print("TravelInfoModel Output:")
    print(travel_model.model_dump_json(indent=2))
    print()

    # CustomerProfileModel - custom types and list processing
    profile_model = CustomerProfileModel(**data)
    print("CustomerProfileModel Output:")
    print(profile_model.model_dump_json(indent=2))
    print()

    # Demonstrate transform override behavior
    print("Override Behavior Test:")
    overridden = CustomerNameModel.model_validate({**data, "full_name": "MANUAL OVERRIDE"})
    print(json.dumps({
        "input": "MANUAL OVERRIDE",
        "output": overridden.full_name,
        "transform_overrides_input": overridden.full_name != "MANUAL OVERRIDE"
    }, indent=2))
    print()

    # Demonstrate various Pydantic instantiation styles
    print("Instantiation Styles Test:")
    m1 = CustomerNameModel.model_validate(data)
    m2 = CustomerNameModel.model_validate_json(open("sample.json").read())
    m3 = CustomerNameModel.model_validate(data, strict=True)
    m4 = CustomerNameModel(**data)
    m5 = CustomerNameModel.model_construct(**data)

    # model_construct skips transforms/validation; computed fields may be missing.
    try:
        m5_full = m5.full_name
    except AttributeError:
        # validate the constructed data to compute transforms
        m5_full = CustomerNameModel.model_validate(m5.model_dump()).full_name

    print(json.dumps({
        "model_validate": m1.full_name,
        "model_validate_json": m2.full_name,
        "strict_mode": m3.full_name,
        "kwargs": m4.full_name,
        "model_construct": m5_full,
        "all_match": all(
            x == m1.full_name for x in [m2.full_name, m3.full_name, m4.full_name, m5_full]
        )
    }, indent=2))

    # Instantiate all models and print prettily
    models = [
        ("CustomerNameModel", CustomerNameModel(**data)),
        ("TravelInfoModel", TravelInfoModel(**data)),
        ("CustomerProfileModel", CustomerProfileModel(**data)),
        ("DocumentSummaryModel", DocumentSummaryModel(**data)),
        ("LocationModel", LocationModel(**data)),
    ]

    for title, model in models:
        print("=" * 60)
        print(f" {title} ".center(60, "="))
        print("=" * 60)
        print(model.model_dump_json(indent=2))
        print()

>>>>>>> Stashed changes

if __name__ == "__main__":
    main()