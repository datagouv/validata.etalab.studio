import pytest
from validata_core import validate


def _schema_compare_columns():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "depenses", "title": "Dépenses", "type": "number"},
            {"name": "recettes", "title": "Recettes", "type": "number"},
        ],
        "custom_checks": [
            {
                "name": "compare-columns-value",
                "params": {"column": "depenses", "op": "<=", "column2": "recettes"},
            }
        ],
    }


@pytest.fixture
def schema_compare_columns():
    return _schema_compare_columns()


def test_compare_columns_value_1(schema_compare_columns):
    source = [["depenses", "recettes"], [12000, 15000]]
    report = validate(source, schema_compare_columns)
    assert report.valid


def test_compare_columns_value_2(schema_compare_columns):
    source = [["depenses", "recettes"], [12000, 12000]]
    report = validate(source, schema_compare_columns)
    assert report.valid


def test_compare_columns_value_3(schema_compare_columns):
    source = [["depenses", "recettes"], [12000, 6000]]
    report = validate(source, schema_compare_columns)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "compare-columns-value"


def test_do_not_apply_compare_columns_value_on_missing_values_on_optional_field1(schema_compare_columns):
    source = [
            [["depenses", "recettes"], [12000, None]],
            [["depenses", "recettes"], [None, 6000]]
        ]
    for s in source:
        report = validate(s, schema_compare_columns)
        assert report.valid


@pytest.fixture
def schema_compare_columns_for_none_value():
    schema_compare_columns_for_none_value = _schema_compare_columns()
    schema_compare_columns_for_none_value["fields"].append({"name": "A", "title": "Field A",
                                                            "type": "string", "constraints": {"required": True}})
    return schema_compare_columns_for_none_value


# To succeed this test, the resource tested needs to have at least one value in row containing None values,
# otherwise, an error 'blank-row' occurs from frictionless and appears in the validation report.
def test_do_not_apply_compare_columns_value_on_missing_values_on_optional_field2(
        schema_compare_columns_for_none_value):
    source_both_none = [["A", "depenses", "recettes"], ["a", None, None]]
    report = validate(source_both_none, schema_compare_columns_for_none_value)
    assert report.valid


@pytest.fixture
def schema_compare_columns_on_required_field():
    schema_compare_columns_on_required_field = _schema_compare_columns()
    schema_compare_columns_on_required_field["fields"][0]["constraints"] = {"required": True}
    return schema_compare_columns_on_required_field


def test_apply_compare_columns_value_on_missing_values_on_required_field(schema_compare_columns_on_required_field):
    source = [["depenses", "recettes"], [None, 6000]]
    report = validate(source, schema_compare_columns_on_required_field)
    print(report)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"


def test_compare_columns_value_validate_start1():
    schema = _schema_compare_columns()
    sources = [
        [["A", "recettes"], [7000, 6000]],
        [["A", "recettes"], [5000, 6000]],
        [["depenses", "B"], [7000, 6000]],
        [["depenses", "B"], [5000, 6000]],
    ]
    expected_messages = [
        f"La colonne {col} n'est pas trouvée" for col in ["depenses", "depenses", "recettes", "recettes"]
    ]

    for source, message in zip(sources, expected_messages):
        report = validate(source, schema=schema)
        assert not report.valid
        assert len(report["tasks"][0]["errors"]) == 1
        assert report["tasks"][0]["errors"][0]["code"] == "check-error"
        assert message in report["tasks"][0]["errors"][0]["message"]


def test_compare_columns_value_validate_start2():
    # All columns relatives to the custom check does not exist -> custom check is ignored
    schema = _schema_compare_columns()
    source = [["A"], [7000]]
    report = validate(source, schema=schema)
    print(report)
    assert report.valid