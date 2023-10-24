import pytest
from validata_core import validate


@pytest.fixture
def schema_opening_hours():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "horaires_ouverture",
                "title": "Horaires d'ouverture",
                "type": "string",
            },
        ],
        "custom_checks": [
            {"name": "opening-hours-value", "params": {"column": "horaires_ouverture"}}
        ],
    }


def test_valid_opening_hours_24_7(schema_opening_hours):
    source = [["horaires_ouverture"], ["24/7"]]
    report = validate(source, schema_opening_hours)
    assert report.valid


def test_valid_opening_hours_Monday_to_Friday(schema_opening_hours):
    source = [["horaires_ouverture"], ["Mo-Fr"]]
    report = validate(source, schema_opening_hours)
    assert report.valid


def test_invalid_opening_hours(schema_opening_hours):
    source = [["horaires_ouverture"], ["Lu-Ve"]]
    report = validate(source, schema_opening_hours)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "opening-hours-value"
    print(report["tasks"][0]["errors"][0])


@pytest.fixture
def schema_opening_hours_for_none_value():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {
                "name": "horaires_ouverture",
                "title": "Horaires d'ouverture",
                "type": "string",
            },
        ],
        "custom_checks": [
            {"name": "opening-hours-value", "params": {"column": "horaires_ouverture"}}
        ],
    }


# To succeed this test, the resource tested needs to have at least one value in row containing None values,
# otherwise, an error 'blank-row' occurs from frictionless and appears in the validation report.
def test_do_not_apply_opening_hours_value_on_missing_values_on_optional_field(schema_opening_hours_for_none_value):
    source = [["A", "horaires_ouverture"], ["a", None]]
    report = validate(source, schema_opening_hours_for_none_value)
    assert report.valid


@pytest.fixture
def schema_opening_hours_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {
                "name": "horaires_ouverture",
                "title": "Horaires d'ouverture",
                "type": "string",
                "constraints": {"required": True}
            },
        ],
        "custom_checks": [
            {"name": "opening-hours-value", "params": {"column": "horaires_ouverture"}}
        ],
    }


def test_apply_opening_hours_value_on_missing_values_on_required_field(schema_opening_hours_on_required_field):
    source = [["A", "horaires_ouverture"], ["a", None]]
    report = validate(source, schema_opening_hours_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"