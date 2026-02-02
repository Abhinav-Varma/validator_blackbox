"""
Consolidated test file covering all functionality.
Only imports from rules.py which contains all models.
"""
import json
from pydantic import ValidationError

from src.rules import CustomerNameModel, TravelInfoModel, CustomerProfileModel


def test_customer_name_model(data):
    """Test CustomerNameModel - pipeline and nested function-call styles"""
    print("=== CustomerNameModel Tests ===\n")

    # Test 1: Basic instantiation
    print("Test 1: Pipeline style transforms")
    profile = CustomerNameModel(**data)
    print(f"  full_name: {profile.full_name}")
    assert profile.full_name is not None
    assert len(profile.full_name) >= 10
    print("  → PASS\n")

    # Test 2: Nested function-call style
    print("Test 2: Nested function-call style")
    print(f"  display_name: {profile.display_name}")
    assert profile.display_name is not None
    print("  → PASS\n")

    # Test 3: Transform override behavior
    print("Test 3: Transform override behavior")
    overridden = CustomerNameModel.model_validate({
        **data,
        "full_name": "MANUAL OVERRIDE",
    })
    print(f"  Input: MANUAL OVERRIDE")
    print(f"  Output: {overridden.full_name}")
    assert "MANUAL OVERRIDE" not in overridden.full_name
    print("  → PASS: Transforms override manual input\n")


def test_travel_info_model(data):
    """Test TravelInfoModel - complex paths and defaults"""
    print("=== TravelInfoModel Tests ===\n")

    # Test 1: Complex nested path extraction
    print("Test 1: Complex nested path extraction")
    travel = TravelInfoModel(**data)
    print(f"  Travel summary: {travel.travel_summary}")
    assert "→" in travel.travel_summary
    print("  → PASS\n")

    # Test 2: Default value when field missing
    print("Test 2: Default value application")
    no_country_data = {k: v for k, v in data.items() if k != "country"}
    no_country = TravelInfoModel.model_validate(no_country_data)
    print(f"  Country (should be 'Unknown'): {no_country.country}")
    assert no_country.country == "Unknown"
    print("  → PASS\n")


def test_customer_profile_model(data):
    """Test CustomerProfileModel - custom types and list processing"""
    print("=== CustomerProfileModel Tests ===\n")

    # Test 1: Custom type validation (PassportNumber)
    print("Test 1: PassportNumber custom type")
    profile = CustomerProfileModel(**data)
    print(f"  Passport: {profile.passport_number}")
    assert profile.passport_number.isalnum()
    assert len(profile.passport_number) <= 9
    print("  → PASS\n")

    # Test 2: Literal type validation
    print("Test 2: Literal type validation")
    print(f"  Gender: {profile.gender}")
    assert profile.gender in ("M", "F", "O")
    print("  → PASS\n")

    # Test 3: NonEmptyStr custom type
    print("Test 3: NonEmptyStr custom type")
    print(f"  Customer name: {profile.customer_name}")
    assert len(profile.customer_name.strip()) > 0
    print("  → PASS\n")

    # Test 4: GST list processing
    print("Test 4: GST list processing")
    print(f"  GST records found: {len(profile.gst_outputs)}")
    for rec in profile.gst_outputs:
        print(f"    - {rec}")
    assert len(profile.gst_outputs) > 0
    print("  → PASS\n")

    # Test 5: Full model dump
    print("Test 5: Full model dump")
    print(profile.model_dump_json(indent=2))
    print("  → PASS\n")


def test_instantiation_styles(data):
    """Test various Pydantic instantiation styles"""
    print("=== Instantiation Styles Test ===\n")

    print("Testing: model_validate, model_validate_json, strict mode, **kwargs")
    m1 = CustomerNameModel.model_validate(data)
    m2 = CustomerNameModel.model_validate_json(open("sample.json").read())
    m3 = CustomerNameModel.model_validate(data, strict=True)
    m4 = CustomerNameModel(**data)
    assert m1.full_name == m2.full_name == m3.full_name == m4.full_name
    print("  → PASS\n")


def main():
    with open("sample.json", "r") as f:
        data = json.load(f)

    test_customer_name_model(data)
    test_travel_info_model(data)
    test_customer_profile_model(data)
    test_instantiation_styles(data)
    print("=== All tests passed! ===")


if __name__ == "__main__":
    main()
