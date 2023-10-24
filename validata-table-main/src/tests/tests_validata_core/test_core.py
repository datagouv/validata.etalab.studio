import pytest
from validata_core import validate
from validata_core.helpers import FileContentValidataResource, ValidataSourceError


@pytest.fixture
def schema_abc():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "A",
                "title": "Field A",
                "type": "string",
                "constraints": {"required": True},
            },
            {"name": "B", "title": "Field B", "type": "string"},
            {"name": "C", "title": "Field C", "type": "string"},
        ],
    }


@pytest.fixture
def schema_date():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [{"name": "A", "title": "Field A", "type": "date"}],
    }


@pytest.fixture
def schema_types_and_required():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "A",
                "title": "Field A",
                "type": "number",
                "constraints": {"required": True},
            },
            {
                "name": "B",
                "title": "Field B",
                "type": "date",
                "constraints": {"required": True},
            },
        ],
    }


@pytest.fixture
def schema_number():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [{"name": "A", "title": "Field A", "type": "number"}],
    }


def validate_csv_bytes(csv_bytes_source, schema):
    validata_source = FileContentValidataResource("foo.csv", csv_bytes_source)
    header, rows = validata_source.extract_tabular_data()
    return validate([header] + rows, schema)


def test_empty_file(schema_abc):
    source = b""
    with pytest.raises(ValidataSourceError):
        validate_csv_bytes(source, schema_abc)


def test_valid_delimiter(schema_abc):
    source = b"""A,B,C
a,b,c"""
    report = validate_csv_bytes(source, schema_abc)
    assert report.valid


def test_valid_delimiter_semicolon(schema_abc):
    source = b"""A;B;C
a;b;c"""
    report = validate_csv_bytes(source, schema_abc)
    assert report.valid


def test_empty_required_value(schema_abc):
    source = [["A", "B", "C"], ["", "b", "c"]]
    report = validate(source, schema_abc)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"


def test_missing_required_column(schema_abc):
    source = [["B", "C"], ["b", "c"]]
    report = validate(source, schema_abc)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "missing-required-header"


def test_missing_column(schema_abc):
    source = [
        ["A", "C"],
        ["a", "c"],
    ]
    schema = {
        "fields": [
            {"name": "A", "constraints": {"required": True}},
            {"name": "B"},
            {"name": "C"},
        ]
    }
    report = validate(source, schema)
    assert report.valid
    assert len(report["tasks"]) == 1
    assert len(report["tasks"][0]["structure_warnings"]) == 1
    assert report["tasks"][0]["structure_warnings"][0]["code"] == "missing-header-warn"


def test_extra_column(schema_abc):
    source = [
        ["A", "D", "B", "C"],
        ["a", "d", "b", "c"],
    ]
    schema = {
        "fields": [
            {"name": "A", "constraints": {"required": True}},
            {"name": "B"},
            {"name": "C"},
        ]
    }
    report = validate(source, schema)
    assert report.valid
    assert len(report["tasks"]) == 1
    assert len(report["tasks"][0]["structure_warnings"]) == 1
    assert report["tasks"][0]["structure_warnings"][0]["code"] == "extra-header-warn"


def test_disordered_columns(schema_abc):
    source = [
        ["C", "A", "B"],
        ["c", "a", "b"],
    ]
    schema = {
        "fields": [
            {"name": "A", "constraints": {"required": True}},
            {"name": "B"},
            {"name": "C"},
        ]
    }
    report = validate(source, schema)
    assert report.valid
    assert len(report["tasks"]) == 1
    assert len(report["tasks"][0]["structure_warnings"]) == 1
    assert (
        report["tasks"][0]["structure_warnings"][0]["code"] == "disordered-header-warn"
    )


def test_ignore_case(schema_abc):
    source = [
        ["AA", "bb", "Cc"],
        ["a", "b", "c"],
    ]

    schema = {
        "fields": [
            {"name": "AA",  "constraints": {"required": True}},
            {"name": "BB",  "constraints": {"required": True}},
            {"name": "CC",  "constraints": {"required": True}},
        ]
    }

    # Test ignore ignore case
    report = validate(source, schema, False)
    assert report.valid
    assert len(report["tasks"]) == 1
    assert len(report["tasks"][0]["structure_warnings"]) == 0

    # Test sensitive to the case
    report = validate(source, schema)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 2
    assert report["tasks"][0]["errors"][0]["code"] == "missing-required-header"
    assert report["tasks"][0]["errors"][0]["message"] == "La colonne obligatoire `BB` est manquante."
    assert report["tasks"][0]["errors"][1]["code"] == "missing-required-header"
    assert report["tasks"][0]["errors"][1]["message"] == "La colonne obligatoire `CC` est manquante."
    assert len(report["tasks"][0]["structure_warnings"]) == 2
    assert report["tasks"][0]["structure_warnings"][0]["code"] == "extra-header-warn"
    assert report["tasks"][0]["structure_warnings"][0]["message"] == \
           "Retirez la colonne `bb` non définie dans le schéma."
    assert report["tasks"][0]["structure_warnings"][1]["code"] == "extra-header-warn"
    assert report["tasks"][0]["structure_warnings"][1]["message"] == \
           "Retirez la colonne `Cc` non définie dans le schéma."

    report = validate(source, schema, True)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 2
    assert len(report["tasks"][0]["structure_warnings"]) == 2
