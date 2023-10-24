import pytest
from validata_core import validate
from validata_core.custom_checks.phone_number_value import is_valid_phone_number


@pytest.fixture
def schema_phone_number():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "telephone",
                "title": "Numéro de téléphone",
                "type": "string",
            },
        ],
        "custom_checks": [
            {"name": "phone-number-value", "params": {"column": "telephone"}}
        ],
    }


# https://en.wikipedia.org/wiki/Fictitious_telephone_number#France


def test_valid_10digits_french_phone_number(schema_phone_number):
    source = [["telephone"], ["02 61 91 13 45"]]
    report = validate(source, schema_phone_number)
    assert report.valid


def test_valid_10digits_french_phone_number_without_spaces(schema_phone_number):
    source = [["telephone"], ["0261911345"]]
    report = validate(source, schema_phone_number)
    assert report.valid


def test_valid_10digits_french_phone_number_with_extra_spaces(schema_phone_number):
    source = [["telephone"], ["  026  191  13  45  "]]
    report = validate(source, schema_phone_number)
    assert report.valid


def test_valid_international_phone_number(schema_phone_number):
    source = [["telephone"], ["+33 2 61 91 13 45"]]
    report = validate(source, schema_phone_number)
    assert report.valid


def test_valid_french_short_phone_number(schema_phone_number):
    source = [["telephone"], ["115"]]
    report = validate(source, schema_phone_number)
    assert report.valid


def test_invalid_legacy_french_phone_number(schema_phone_number):
    source = [["telephone"], ["619 13 45"]]
    report = validate(source, schema_phone_number)
    assert not report.valid


def test_several_phone_numbers(schema_phone_number):

    for phonenumber in [
        "3949",
        "39490",
        "0601020304",
        "0601020304",
        "+3361020304",
        "+33601020304",
    ]:
        print(f"{phonenumber} -> {is_valid_phone_number(phonenumber)}")


@pytest.fixture
def schema_phone_number_for_none_value():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {
                "name": "telephone",
                "title": "Numéro de téléphone",
                "type": "string",
            },
        ],
        "custom_checks": [
            {"name": "phone-number-value", "params": {"column": "telephone"}}
        ],
    }


# To succeed this test, the resource tested needs to have at least one value in row containing None values,
# otherwise, an error 'blank-row' occurs from frictionless and appears in the validation report.
def test_do_not_apply_french_phone_number_on_missing_values_on_optional_field(schema_phone_number_for_none_value):
    source = [["A", "telephone"], ["a", None]]
    report = validate(source, schema_phone_number_for_none_value)
    assert report.valid


@pytest.fixture
def schema_phone_number_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {
                "name": "telephone",
                "title": "Numéro de téléphone",
                "type": "string",
                "constraints": {"required": True}
            },
        ],
        "custom_checks": [
            {"name": "phone-number-value", "params": {"column": "telephone"}}
        ],
    }


def test_apply_french_phone_number_on_missing_values_on_required_field(schema_phone_number_on_required_field):
    source = [["A", "telephone"], ["a", None]]
    report = validate(source, schema_phone_number_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"
