"""
Demonstration script (no pytest) showing that field transforms
override manual input-provided values.

Run:
    python -m src.override_demo
"""
import json
from src.rules import NameModel, CustomerVisaProfileModel


def main() -> None:
    with open("sample.json", "r") as f:
        data = json.load(f)

    computed = NameModel.model_validate(data).full_name
    overridden_input = {**data, "full_name": "MANUAL OVERRIDE"}
    overridden_output = NameModel.model_validate(overridden_input).full_name

    print("Computed full_name:", computed)
    print("Manual input full_name:", overridden_input["full_name"])
    print("Model output with manual override input:", overridden_output)
    print("Transforms override manual input?:", computed == overridden_output)

    # Also show a full model dump for visibility
    print()
    print("CustomerVisaProfileModel dump with manual override present:")
    print(CustomerVisaProfileModel.model_validate(overridden_input).model_dump())


if __name__ == "__main__":
    main()
