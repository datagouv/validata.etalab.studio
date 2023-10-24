import pytest
from validata_core import validate


def _schema_cohesive_columns():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "id", "title": "Identifiant", "type": "number"},
            {"name": "col1", "title": "Colonne 1", "type": "string"},
            {"name": "col2", "title": "Colonne 2", "type": "string"},
        ],
        "custom_checks": [
            {
                "name": "cohesive-columns-value",
                "params": {"column": "col1", "othercolumns": ["col2"]},
            }
        ],
    }


@pytest.fixture
def schema_cohesive_columns():
    return _schema_cohesive_columns()


def test_cohesive_columns_values_1(schema_cohesive_columns):
    source = [["id", "col1", "col2"], [1, None, None]]

    report = validate(source, schema_cohesive_columns)
    assert report.valid


def test_cohesive_columns_values_2(schema_cohesive_columns):
    source = [["id", "col1", "col2"], [1, "foo", "bar"]]

    report = validate(source, schema_cohesive_columns)
    assert report.valid


def test_cohesive_columns_values_3(schema_cohesive_columns):
    source = [["id"], [1]]

    report = validate(source, schema_cohesive_columns)
    print(report)
    assert report.valid


def test_cohesive_columns_values_4(schema_cohesive_columns):
    source = [["id", "col1", "col2"], [1, "foo", None]]

    report = validate(source, schema_cohesive_columns)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "cohesive-columns-value"


def test_cohesive_columns_values_5(schema_cohesive_columns):
    source = [["id", "col1", "col2"], [1, None, "bar"]]

    report = validate(source, schema_cohesive_columns)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "cohesive-columns-value"


@pytest.fixture
def schema_cohesive_columns_on_required_field():
    schema_cohesive_on_required_field = _schema_cohesive_columns()
    schema_cohesive_on_required_field["fields"][1]["constraints"] = {"required": True}
    return schema_cohesive_on_required_field


def test_cohesive_columns_values_required(schema_cohesive_columns_on_required_field):
    source = [["id", "col1", "col2"], [1, None, "bar"]]
    report = validate(source, schema_cohesive_columns_on_required_field)
    assert not report.valid
    print(report)
    assert report["stats"]["errors"] == 2
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"
    assert report["tasks"][0]["errors"][1]["code"] == "cohesive-columns-value"


def test_cohesive_columns_values_required_missing_columns1(schema_cohesive_columns_on_required_field):
    # One on the column relative to the custom check does not exist -> validation error
    source = [["id", "col1"], [1, "foo"]]
    report = validate(source, schema_cohesive_columns_on_required_field)
    print(report)
    assert not report.valid
    expected_message = "'cohesive-columns-value': La colonne à comparer 'col2' est manquante"
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "check-error"
    assert expected_message in report["tasks"][0]["errors"][0]["message"]


def test_cohesive_columns_values_required_missing_columns2(schema_cohesive_columns_on_required_field):
    # One on the column relative to the custom check and required does not exist -> validation error
    source = [["id", "col2"], [1, "bar"]]
    report = validate(source, schema_cohesive_columns_on_required_field)
    print(report)
    assert not report.valid
    expected_message = "'cohesive-columns-value': La colonne 'col1' est manquante"
    assert len(report["tasks"][0]["errors"]) == 2
    assert report["tasks"][0]["errors"][0]["code"] == "missing-required-header"
    assert report["tasks"][0]["errors"][1]["code"] == "check-error"
    assert expected_message in report["tasks"][0]["errors"][1]["message"]


def test_cohesive_columns_values_required_missing_columns3(schema_cohesive_columns_on_required_field):
    # All columns relatives to the custom check does not exist -> custom check is ignored
    source = [["id", "col2"], [1, "bar"]]
    report = validate(source, schema_cohesive_columns_on_required_field)
    print(report)
    assert not report.valid
