# src/test.py
from typing import Optional

from pydantic import ValidationError

from src.custom_basemodel import TransformBaseModel, Field
from src.step_engine import path


class TransformOrderTest(TransformBaseModel):
    name: str = Field(
        description="Uppercased name",
        transform=path("$.name") | str.upper,
    )

    age: int = Field(
        description="Must be int after transform",
        transform=path("$.age"),
    )

    country: str = Field(
        default="Unknown",
        description="Default applies if transform returns None",
        transform=path("$.country"),
    )

    score: int = Field(
        description="Required field – must be provided",
        transform=path("$.score"),
    )


def test_transform_order():
    print("=== Transform order & validation test ===\n")

    # ────────────────────────────────────────────────
    # Case 1: All good – transform + coercion succeed
    # ────────────────────────────────────────────────
    good = {
        "name": "alice",
        "age": "28",           # string → should become int
        "country": "Canada",
        "score": 95,
    }

    print("Case 1: good data")
    print("Input dict before validation:", good)
    m = TransformOrderTest.model_validate(good)
    print("Result after validation:", m.model_dump())
    assert m.name == "ALICE", "Name transform failed"
    assert m.age == 28, "Age coercion failed"
    assert m.country == "Canada"
    assert m.score == 95
    print("→ PASS\n")

    # ────────────────────────────────────────────────
    # Case 2: Required field missing after transform
    # ────────────────────────────────────────────────
    missing_score = {
        "name": "bob",
        "age": 33,
        "country": "Germany",
        # no score → transform returns None → should fail required check
    }

    print("Case 2: required field 'score' missing")
    print("Input dict before validation:", missing_score)
    try:
        m = TransformOrderTest.model_validate(missing_score)
        print("FAIL: should have raised ValidationError")
    except ValidationError as e:
        print("ValidationError (expected):", e.errors(include_url=False))
        assert any("score" in str(err["loc"]) for err in e.errors())
        print("→ PASS: validation not circumvented\n")

    # ────────────────────────────────────────────────
    # Case 3: Invalid type after transform
    # ────────────────────────────────────────────────
    bad_age = {
        "name": "charlie",
        "age": "thirty",       # cannot be coerced to int
        "country": "Australia",
        "score": 88,
    }

    print("Case 3: invalid type for age")
    print("Input dict before validation:", bad_age)
    try:
        m = TransformOrderTest.model_validate(bad_age)
        print("FAIL: should have raised ValidationError")
    except ValidationError as e:
        print("ValidationError (expected):", e.errors(include_url=False))
        assert any("age" in str(err["loc"]) for err in e.errors())
        assert any("int" in str(err["msg"]) for err in e.errors())
        print("→ PASS: type validation enforced\n")

    # ────────────────────────────────────────────────
    # Case 4: Transform returns None → default applies
    # ────────────────────────────────────────────────
    no_country = {
        "name": "diana",
        "age": 41,
        "score": 100,
        # no country → transform → None → default should apply
    }

    print("Case 4: transform returns None for country")
    print("Input dict before validation:", no_country)
    m = TransformOrderTest.model_validate(no_country)
    print("Result after validation:", m.model_dump())
    assert m.country == "Unknown", "Default not applied"
    print("→ PASS: default applied when transform returned None\n")


if __name__ == "__main__":
    test_transform_order()