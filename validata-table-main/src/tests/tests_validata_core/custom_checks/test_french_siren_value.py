import pytest
from validata_core import validate


@pytest.fixture
def schema_required_and_custom_check():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "siren",
                "title": "N° SIREN",
                "type": "string",
                "constraints": {"required": True},
            },
            {
                "name": "B",
                "title": "Field B",
                "type": "string",
                "constraints": {"required": True},
            },
            {"name": "C", "title": "Field C", "type": "string"},
        ],
        "custom_checks": [
            {"name": "french-siren-value", "params": {"column": "siren"}}
        ],
    }


@pytest.fixture
def schema_siren():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "id", "title": "id", "type": "number"},
            {"name": "siren", "title": "Numéro SIREN", "type": "string"},
        ],
        "custom_checks": [
            {"name": "french-siren-value", "params": {"column": "siren"}}
        ],
    }


def test_missing_required_header_and_custom_check(schema_required_and_custom_check):
    source = [["siren", "C"], ["226500015", "c"]]
    report = validate(source, schema_required_and_custom_check)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "missing-required-header"


def test_valid_custom_check_siren(schema_siren):
    source = [["id", "siren"], [1, "529173189"]]
    report = validate(source, schema_siren)
    assert report.valid


def test_invalid_custom_check_siren(schema_siren):
    source = [["id", "siren"], [1, "529173188"]]
    report = validate(source, schema_siren)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "french-siren-value"


def test_do_not_apply_french_siren_value_on_missing_values_on_optional_field(schema_siren):
    source = [["id", "siren"], [1, None]]
    report = validate(source, schema_siren)
    assert report.valid


def test_do_not_apply_french_siren_value_on_missing_column_on_optional_field(schema_siren):
    # Column relative to the custom check does not exist -> custom check is ignored
    source = [["id"], [1]]
    report = validate(source, schema_siren)
    assert report.valid


@pytest.fixture
def schema_siren_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "id", "title": "id", "type": "number"},
            {"name": "siren", "title": "Numéro SIREN", "type": "string", "constraints": {"required": True}},
        ],
        "custom_checks": [
            {"name": "french-siren-value", "params": {"column": "siren"}}
        ],
    }


def test_french_siren_value_on_missing_values_on_required_field(schema_siren_on_required_field):
    source = [["id", "siren"], [1, None]]
    report = validate(source, schema_siren_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"


def test_french_siren_value_with_missing_column(schema_siren_on_required_field):
    source = [["id"], [1]]
    report = validate(source, schema_siren_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "missing-required-header"
