import json
from pathlib import Path

import pytest
from validata_core import validate
from validata_core.helpers import FileContentValidataResource, URLValidataResource


def validate_xlsx_bytes(bytes_source_content, schema):
    validata_source = FileContentValidataResource("foo.xlsx", bytes_source_content)
    header, rows = validata_source.extract_tabular_data()
    return validate([header] + rows, schema)


@pytest.fixture()
def dae_schema():
    with Path("tests/tests_validata_core/fixtures/dae_schema.json").open("rt", encoding="utf-8") as fd:
        return json.load(fd)


def test_validate_dae_xlsx_file(dae_schema):
    with Path("tests/tests_validata_core/fixtures/dae_test.xlsx").open("rb") as fd:
        bytes_content = fd.read()

    validata_source = FileContentValidataResource("dae_test.xlsx", bytes_content)
    header, rows = validata_source.extract_tabular_data()
    report = validate([header] + rows, dae_schema)
    assert report.valid


def test_validate_dae_xlsx_url(dae_schema):

    validata_source = URLValidataResource(
        "https://gitlab.com/validata-table/validata-ui/uploads/dc50b16c803e2e2d61a645019cd75b3c/test1.xlsx"
    )
    header, rows = validata_source.extract_tabular_data()
    report = validate([header] + rows, dae_schema)
    assert report.valid
