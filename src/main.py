"""
Entry point: load JSON, run through models defined in rules.py, print outputs.
Demonstrates both instantiation styles:
1. Model.model_validate(data)
2. Model(**data)
"""
import json
from src.rules import CustomerNameModel, TravelInfoModel, CustomerProfileModel


def main() -> None:
    with open("sample.json", "r") as f:
        data = json.load(f)

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
    print(json.dumps({
        "model_validate": m1.full_name,
        "model_validate_json": m2.full_name,
        "strict_mode": m3.full_name,
        "kwargs": m4.full_name,
        "all_match": m1.full_name == m2.full_name == m3.full_name == m4.full_name
    }, indent=2))


if __name__ == "__main__":
    main()
