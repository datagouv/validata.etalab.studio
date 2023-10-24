from pathlib import Path

import pytest
from validata_core import validate


@pytest.fixture
def array_schema():
    return {
        "$schema": "https://specs.frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "array_field",
                "title": "Array field",
                "description": "Array field description",
                "type": "array",
                "arrayItem": {"constraints": {"enum": ["a", "b"]}},
            }
        ],
    }


def test_validate_ko(array_schema):
    report = validate(Path("tests/tests_validata_core/fixtures/invalid_array.csv"), array_schema)
    assert report.stats["errors"] == 2
    assert report.tasks[0]["errors"][0].code == "constraint-error"
    assert report.tasks[0]["errors"][1].code == "constraint-error"
    assert not report.valid


def test_validate_ok(array_schema):
    report = validate(Path("tests/tests_validata_core/fixtures/valid_array.csv"), array_schema)
    assert report.valid
