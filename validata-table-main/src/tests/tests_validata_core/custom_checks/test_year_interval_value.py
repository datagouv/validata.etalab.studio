import pytest
from validata_core import validate


@pytest.fixture
def schema_year_interval():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "projet", "title": "Projet", "type": "string"},
            {"name": "annee", "title": "Année(s)", "type": "string"},
        ],
        "custom_checks": [
            {"name": "year-interval-value", "params": {"column": "annee"}}
        ],
    }


@pytest.fixture
def schema_year_interval_allow_year_only():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "projet", "title": "Projet", "type": "string"},
            {"name": "annee", "title": "Année(s)", "type": "string"},
        ],
        "custom_checks": [
            {
                "name": "year-interval-value",
                "params": {"column": "annee", "allow-year-only": "true"},
            }
        ],
    }


def test_valid_custom_check_year_interval_1(schema_year_interval):
    source = [["projet", "annee"], ["Validata", "2018/2020"]]
    report = validate(source, schema_year_interval)
    assert report.valid


def test_valid_custom_check_year_interval_2(schema_year_interval_allow_year_only):
    source = [["projet", "annee"], ["Validata", "2018/2020"]]
    report = validate(source, schema_year_interval_allow_year_only)
    assert report.valid


def test_valid_custom_check_year_interval_3(schema_year_interval_allow_year_only):
    source = [["projet", "annee"], ["Validata", "2020"]]
    report = validate(source, schema_year_interval_allow_year_only)
    assert report.valid


def test_invalid_custom_check_year_interval_1(schema_year_interval):
    source = [["projet", "annee"], ["Validata", "foobar"]]
    report = validate(source, schema_year_interval)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "year-interval-value"


def test_invalid_custom_check_year_interval_2(schema_year_interval):
    source = [["projet", "annee"], ["Validata", "2017/2017"]]
    report = validate(source, schema_year_interval)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "year-interval-value"


def test_invalid_custom_check_year_interval_3(schema_year_interval):
    source = [["projet", "annee"], ["Validata", "2017/2016"]]
    report = validate(source, schema_year_interval)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "year-interval-value"


def test_do_not_apply_year_internal_value_on_missing_values_on_optional_field(schema_year_interval):
    source = [["projet", "annee"], ["Validata", None]]
    report = validate(source, schema_year_interval)
    assert report.valid


@pytest.fixture
def schema_year_interval_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "projet", "title": "Projet", "type": "string"},
            {"name": "annee", "title": "Année(s)", "type": "string", "constraints": {"required": True}},
        ],
        "custom_checks": [
            {"name": "year-interval-value", "params": {"column": "annee"}}
        ],
    }


def test_apply_year_internal_value_on_missing_values_on_required_field(schema_year_interval_on_required_field):
    source = [["projet", "annee"], ["Validata", None]]
    report = validate(source, schema_year_interval_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"