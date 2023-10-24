import pytest
from validata_core import validate


@pytest.fixture
def schema_siret():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "id", "title": "id", "type": "number"},
            {"name": "numero_siret", "title": "Numéro SIRET", "type": "string"},
        ],
        "custom_checks": [
            {"name": "french-siret-value", "params": {"column": "numero_siret"}}
        ],
    }


def test_valid_custom_check_siret(schema_siret):
    source = [["id", "numero_siret"], [1, "83014132100026"]]
    report = validate(source, schema_siret)
    assert report.valid


def test_invalid_custom_check_siret(schema_siret):
    source = [["id", "numero_siret"], [1, "529173188"]]
    report = validate(source, schema_siret)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "french-siret-value"


def test_do_not_apply_french_siret_value_on_missing_values_on_optional_field(schema_siret):
    source = [["id", "numero_siret"], [1, None]]
    report = validate(source, schema_siret)
    assert report.valid


@pytest.fixture
def schema_siret_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "id", "title": "id", "type": "number"},
            {"name": "numero_siret", "title": "Numéro SIRET", "type": "string", "constraints": {"required": True}},
        ],
        "custom_checks": [
            {"name": "french-siret-value", "params": {"column": "numero_siret"}}
        ],
    }


def test_french_siret_value_on_missing_values_on_required_field(schema_siret_on_required_field):
    source = [["id", "numero_siret"], [1, None]]
    report = validate(source, schema_siret_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"
