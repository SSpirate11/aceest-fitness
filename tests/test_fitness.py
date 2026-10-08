from datetime import date

import pytest

from aceest import fitness


@pytest.mark.parametrize("code,weight,expected", [
    ("FL", 70, 1540), ("MG", 80, 2800), ("BG", 60, 1560), ("fl", 50, 1100),
])
def test_calculate_calories(code, weight, expected):
    assert fitness.calculate_calories(weight, code) == expected


@pytest.mark.parametrize("weight", [0, -5])
def test_calories_rejects_non_positive_weight(weight):
    with pytest.raises(ValueError):
        fitness.calculate_calories(weight, "FL")


def test_calories_rejects_unknown_program():
    with pytest.raises(ValueError):
        fitness.calculate_calories(70, "XYZ")


@pytest.mark.parametrize("weight,height,category", [
    (50, 180, "Underweight"), (70, 175, "Normal"),
    (85, 175, "Overweight"), (110, 170, "Obese"),
])
def test_bmi_categories(weight, height, category):
    _, result = fitness.calculate_bmi(weight, height)
    assert result == category


def test_bmi_value_is_rounded():
    assert fitness.calculate_bmi(70, 175) == (22.9, "Normal")


def test_bmi_rejects_invalid_input():
    with pytest.raises(ValueError):
        fitness.calculate_bmi(70, 0)


def test_get_program_is_case_insensitive():
    assert fitness.get_program("mg")["name"] == "Muscle Gain"
    assert fitness.get_program("nope") is None
    assert fitness.get_program(None) is None


@pytest.mark.parametrize("code,level,focus,days", [
    ("FL", "beginner", "Conditioning", 3),
    ("MG", "intermediate", "Hypertrophy", 4),
    ("BG", "advanced", "Full Body", 5),
])
def test_generate_program_structure(code, level, focus, days):
    result = fitness.generate_program(code, level, seed=42)
    assert result["focus"] == focus
    assert result["days"] == days
    assert len({item["day"] for item in result["plan"]}) == days
    sets_range = fitness.LEVELS[level]["sets"]
    for item in result["plan"]:
        assert item["exercise"] in fitness.EXERCISE_POOL[focus]
        assert sets_range[0] <= item["sets"] <= sets_range[1]


def test_generate_program_is_deterministic_with_seed():
    assert fitness.generate_program("FL", "beginner", seed=1) == \
        fitness.generate_program("FL", "beginner", seed=1)


def test_generate_program_rejects_bad_level():
    with pytest.raises(ValueError):
        fitness.generate_program("FL", "expert")


def test_membership_status():
    today = date(2026, 1, 15)
    assert fitness.membership_status("2026-02-01", today) == "Active"
    assert fitness.membership_status("2026-01-01", today) == "Expired"
    assert fitness.membership_status(None, today) == "Unknown"
    assert fitness.membership_status("not-a-date", today) == "Unknown"

