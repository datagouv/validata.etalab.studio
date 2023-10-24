import pytest
from validata_core import validate


@pytest.fixture
def schema_nomenclature_actes_value():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [{"name": "acte", "title": "Acte", "type": "string"}],
        "custom_checks": [
            {"name": "nomenclature-actes-value", "params": {"column": "acte"}}
        ],
    }


def test_valid_nomenclature_actes_value(schema_nomenclature_actes_value):
    source = [["acte"], ["Fonction publique/foobar"]]

    report = validate(source, schema_nomenclature_actes_value)
    assert report.valid


def test_valid_nomenclature_actes_value_multi_case(schema_nomenclature_actes_value):
    source = [["acte"], ["fOnCtIOn pubLIQUE/foobar"]]

    report = validate(source, schema_nomenclature_actes_value)
    assert report.valid


def test_invalid_nomenclature_actes_value_1(schema_nomenclature_actes_value):
    source = [["acte"], ["foobar"]]

    report = validate(source, schema_nomenclature_actes_value)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "nomenclature-actes-value"
    assert "est manquant" in report["tasks"][0]["errors"][0]["message"]


def test_invalid_nomenclature_actes_value_2(schema_nomenclature_actes_value):
    source = [["acte"], ["Baz/foobar"]]

    report = validate(source, schema_nomenclature_actes_value)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "nomenclature-actes-value"
    assert "pas reconnu" in report["tasks"][0]["errors"][0]["message"]


def test_invalid_nomenclature_actes_value_spaces_around(
    schema_nomenclature_actes_value,
):
    source = [["acte"], ["Fonction publique / truc"]]

    report = validate(source, schema_nomenclature_actes_value)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "nomenclature-actes-value"
    print(report["tasks"][0]["errors"][0]["message"])
    assert "pas être précédé" in report["tasks"][0]["errors"][0]["message"]


def test_invalid_nomenclature_actes_value_space_after(schema_nomenclature_actes_value):
    source = [["acte"], ["Fonction publique/ truc"]]

    report = validate(source, schema_nomenclature_actes_value)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "nomenclature-actes-value"
    print(report["tasks"][0]["errors"][0]["message"])
    assert "pas être précédé" in report["tasks"][0]["errors"][0]["message"]


@pytest.fixture
def schema_nomenclature_actes_for_none_value():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {"name": "acte", "title": "Acte", "type": "string"}
        ],
        "custom_checks": [
            {"name": "nomenclature-actes-value", "params": {"column": "acte"}}
        ],
    }


# To succeed this test, the resource tested needs to have at least one value in row containing None values,
# otherwise, an error 'blank-row' occurs from frictionless and appears in the validation report.
def test_do_not_apply_nomenclature_actes_value_on_missing_values_on_optional_field(
        schema_nomenclature_actes_for_none_value):
    source = [["A", "acte"], ["a", None]]
    report = validate(source, schema_nomenclature_actes_for_none_value)
    assert report.valid


@pytest.fixture
def schema_nomenclature_actes_value_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {"name": "acte", "title": "Acte", "type": "string", "constraints": {"required": True}}
        ],
        "custom_checks": [
            {"name": "nomenclature-actes-value", "params": {"column": "acte"}}
        ],
    }


def test_apply_nomenclature_actes_value_on_missing_values_on_required_field(
        schema_nomenclature_actes_value_on_required_field):
    source = [["A", "acte"], ["a", None]]
    report = validate(source, schema_nomenclature_actes_value_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"
