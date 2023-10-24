import pytest
from validata_core import validate


@pytest.fixture()
def schema_with_orphan_custom_check():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "siren",
                "title": "Numéro SIREN",
                "type": "string",
                "constraints": {"required": True}
            }
        ],
        "custom_checks": [
            {"name": "french-siren-value", "params": {"column": "siren"}}
        ],
    }


@pytest.fixture()
def schema_with_unknown_custom_check():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "siren",
                "title": "Numéro SIREN",
                "type": "string",
            }
        ],
        "custom_checks": [{"name": "foo-siren-value", "params": {"column": "sirene"}}],
    }


@pytest.fixture()
def schema_with_non_existing_primary_key():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "a",
            }
        ],
        "primaryKey": ["b"],
    }


@pytest.fixture()
def schema_with_existing_primary_key():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "a",
            }
        ],
        "primaryKey": ["a"],
    }


def test_schema_with_orphan_custom_checks(schema_with_orphan_custom_check):
    source = [["sirene"], ["529173189"]]
    report = validate(source, schema_with_orphan_custom_check)
    assert not report.valid

    # Error doesn't appear in error common list
    assert len(report.errors) == 0

    # but in task errors
    assert len(report.tasks[0].errors) == 1

    # as a 'missing-required-header error'
    assert report.tasks[0].errors[0]["code"] == "missing-required-header"


def test_schema_with_unknown_custom_checks(schema_with_unknown_custom_check):
    source = [["siren"], ["529173189"]]
    report = validate(source, schema_with_unknown_custom_check)
    assert not report.valid

    # Error doesn't appear in the list of errors not associated with a table
    assert len(report.errors) == 0

    # but in task errors
    assert len(report.tasks[0].errors) == 1

    # as a 'check-error'
    assert report.tasks[0].errors[0]["code"] == "check-error"

    # and in the errors stats
    assert report.stats['errors'] == 1

    # What about 2 errors in the custom checks ?
    schema_with_unknown_custom_check['custom_checks'].append(
        {"name": "unknown2", "params": {"column": "siren"}})
    report = validate(source, schema_with_unknown_custom_check)
    assert report.stats['errors'] == 2


def test_primary_key_schema(schema_with_non_existing_primary_key):
    source = [["a"], ["foo"]]

    report = validate(source, schema_with_non_existing_primary_key)
    assert not report.valid

    # Error doesn't appear in error common list
    assert len(report.errors) == 0

    # but in task errors
    assert report["tasks"][0]["errors"]

    # as a 'schema-error'
    assert report["tasks"][0]["errors"][0]["code"] == "schema-error"


def test_primary_key_schema_2(schema_with_existing_primary_key):
    source = [["b"], ["foo"]]
    report = validate(source, schema_with_existing_primary_key)
    assert not report.valid

    # Error doesn't appear in error common list
    assert len(report.errors) == 0

    # but in task errors
    assert report["tasks"][0]["errors"]

    # as a 'schema-error'
    assert report["tasks"][0]["errors"][0]["code"] == "schema-error"
