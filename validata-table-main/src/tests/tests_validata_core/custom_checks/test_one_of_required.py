import pytest
from validata_core import validate


@pytest.fixture
def schema_one_of_required():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "id", "title": "Identifiant", "type": "number"},
            {"name": "A", "title": "Colonne A", "type": "string"},
            {"name": "B", "title": "Colonne B", "type": "string"},
        ],
        "custom_checks": [
            {
                "name": "one-of-required",
                "params": {"column1": "A", "column2": "B"},
            }
        ],
    }


def test_one_of_required_valid(schema_one_of_required):
    # Test cases expecting valid reports
    sources = [
        [["id", "A"], [1, "a"]],
        [["id", "B"], [1, "b"]],
        [["id", "A", "B"], [1, "a", "b"]],
        [["id", "A", "B"], [1, "a", None]],
        [["id", "A", "B"], [1, None, "b"]],
    ]

    for source in sources:
        report = validate(source, schema_one_of_required)
        assert report.valid


def test_one_of_required_invalid_row(schema_one_of_required):
    # Test cases expecting invalid reports with error of one-of-required custom check and message :
    # "Au moins l'une des colonnes 'A' ou 'B' doit comporter une valeur."
    # (Indirectly tests validate_row method)

    sources = [
        [["id", "A"], [1, None]],
        [["id", "B"], [1, None]],
        [["id", "A", "B"], [1, None, None]],
    ]
    for source in sources:
        report = validate(source, schema_one_of_required)
        errors = report["tasks"][0]["errors"]
        assert not report.valid
        assert len(errors) == 1
        assert report["stats"]["errors"] == 1
        assert report["stats"]["tasks"] == 1
        assert errors[0]["code"] == "one-of-required"
        assert "Au moins l'une des colonnes 'A' ou 'B' doit comporter une valeur." in errors[0]["message"]


def test_one_of_required_missing_columns(schema_one_of_required):
    # Test cases expecting invalid reports with error of one-of-required custom check and message :
    # "Les colonnes 'A' et 'B' sont manquantes."
    # (Indirectly tests validate_start method)
    source = [["id"], [1]]
    report = validate(source, schema_one_of_required)
    errors = report["tasks"][0]["errors"]
    assert not report.valid
    assert len(errors) == 1
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1
    assert errors[0]["code"] == "one-of-required"
    assert "Une des deux colonnes requises : Les deux colonnes 'A' et 'B' sont manquantes." in report["tasks"][0]["errors"][0]["message"]
