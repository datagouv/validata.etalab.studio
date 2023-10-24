import pytest
from validata_core import validate


def _schema_sum_columns_value(column_list=["chauffage", "salaires", "fraisdebouche"]):
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "charges", "title": "Charges", "type": "number"},
            {"name": "chauffage", "title": "Chauffage", "type": "number"},
            {"name": "salaires", "title": "Salaires", "type": "number"},
            {"name": "fraisdebouche", "title": "Frais de bouche", "type": "number"},
        ],
        "custom_checks": [
            {
                "name": "sum-columns-value",
                "params": {"column": "charges", "columns": column_list},
            }
        ],
    }


@pytest.fixture
def schema_sum_columns_value_ok():
    return _schema_sum_columns_value()


def test_valid_custom_sum_columns_value_1(schema_sum_columns_value_ok):
    source = [
        ["charges", "chauffage", "salaires", "fraisdebouche"],
        [12000, 600, 4000, 7400],
    ]
    report = validate(source, schema_sum_columns_value_ok)
    assert report.valid


def test_valid_custom_sum_columns_value_2(schema_sum_columns_value_ok):
    source = [
        ["charges", "chauffage", "salaires", "fraisdebouche"],
        [12000, 600, None, 7400],
    ]
    report = validate(source, schema_sum_columns_value_ok)
    assert report.valid


def test_valid_custom_sum_columns_value_3(schema_sum_columns_value_ok):
    source = [
        ["charges", "chauffage", "salaires", "fraisdebouche"],
        [None, 600, 4000, 7400],
    ]
    report = validate(source, schema_sum_columns_value_ok)
    assert report.valid


def test_valid_custom_sum_columns_value_4(schema_sum_columns_value_ok):
    # 1100 != 600 + 4000 + 7400
    source = [
        ["charges", "chauffage", "salaires", "fraisdebouche"],
        [1100, 600, 4000, 7400],
    ]
    report = validate(source, schema_sum_columns_value_ok)
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert report["tasks"][0]["errors"][0]["code"] == "sum-columns-value"


# TODO: add other test cases for sum_column_values


def test_do_not_apply_sum_columns_value_on_missing_values_on_optional_field(schema_sum_columns_value_ok):
    source = [
        [["charges", "chauffage", "salaires", "fraisdebouche"], [None, 600, 4000, 7400]],
        [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, 4000, 7400]],
        [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, 600, None, 7400]],
        [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, 600, 4000, None]],
        [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, 4000, 7400]],
        [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, None, 7400]],
        [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, None, None]],
    ]

    for s in source:
        report = validate(s, schema_sum_columns_value_ok)
        assert report.valid


@pytest.fixture
def schema_sum_columns_value_on_required_field(column_list=["chauffage", "salaires", "fraisdebouche"]):
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "charges", "title": "Charges", "type": "number"},
            {"name": "chauffage", "title": "Chauffage", "type": "number", "constraints": {"required": True}},
            {"name": "salaires", "title": "Salaires", "type": "number"},
            {"name": "fraisdebouche", "title": "Frais de bouche", "type": "number"},
        ],
        "custom_checks": [
            {
                "name": "sum-columns-value",
                "params": {"column": "charges", "columns": column_list},
            }
        ],
    }


def test_apply_sum_columns_value_on_missing_values_on_required_field(schema_sum_columns_value_on_required_field):
    # empty cell on required field : unvalid report
    source = [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, 4000, 7400]]
    report = validate(source, schema_sum_columns_value_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"

    # empty cell on optional field related to  sum_columns_value custom_check : valid report
    source1 = [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, 600, None, 7400]]
    report = validate(source1, schema_sum_columns_value_on_required_field)
    assert report.valid

    source2 = [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, 600, 4000, None]]
    report = validate(source2, schema_sum_columns_value_on_required_field)
    assert report.valid

    # empty cell on required field and on optional field related to sum_columns_value custom_check : unvalid report
    source1 = [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, None, 7400]]
    report = validate(source1, schema_sum_columns_value_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"

    source2 = [["charges", "chauffage", "salaires", "fraisdebouche"], [12000, None, 4000, None]]
    report = validate(source2, schema_sum_columns_value_on_required_field)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"


def test_sum_columns_value_validate_start1():
    schema = _schema_sum_columns_value()
    sources = [
        [["charg", "chauffage", "salaires", "fraisdebouche"], [11000, 600, 4000, 7400]],  # custom-check-error is ignored because validate_start generates a check-error
        [["charges", "chauf", "salaires", "fraisdebouche"], [12000, 600, 4000, 7400]],
        [["charges", "chauffage", "salair", "fraisdebouche"], [12000, 600, 4000, 7400]],
        [["charges", "chauffage", "salaires", "fraisde"], [12000, 600, 4000, 7400]]
    ]
    expected_messages = [
        f"la colonne {col} n'est pas trouvée" for col in ["charges", "chauffage", "salaires", "fraisdebouche"]
    ]

    for source, message in zip(sources, expected_messages):
        report = validate(source, schema=schema)
        assert not report.valid
        assert len(report["tasks"][0]["errors"]) == 1
        assert report["tasks"][0]["errors"][0]["code"] == "check-error"
        assert message in report["tasks"][0]["errors"][0]["message"]


def test_sum_columns_value_validate_start2():
    # All columns relatives to the custom check does not exist -> custom check is ignored
    schema = _schema_sum_columns_value()
    source = [["A"], ["a"]]
    report = validate(source, schema=schema)
    print(report)
    assert report.valid
