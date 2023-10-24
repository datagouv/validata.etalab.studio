import pytest
from validata_core.helpers import (
    FileContentValidataResource,
    ValidataResource,
    ValidataSourceError,
)


@pytest.fixture
def irve_accent_valide_content():
    return open("tests/tests_validata_core/fixtures/irve_accent_valide.csv", "rb").read()


@pytest.fixture
def irve_driveco_content():
    return open("tests/tests_validata_core/fixtures/irve-driveco-201215.csv", "rb").read()


@pytest.fixture
def with_bom_content():
    return open("tests/tests_validata_core/fixtures/sample_with_bom.csv", "rb").read()


@pytest.fixture
def invalid_utf16_content():
    return open("tests/tests_validata_core/fixtures/mini-menus-collectifs_invalide.utf-16.csv", "rb").read()


def test_detect_utf_8(irve_accent_valide_content):
    b_content = irve_accent_valide_content
    assert ValidataResource.detect_encoding(b_content) == "utf-8"


def test_read_utf_8(irve_accent_valide_content):
    head, rows = FileContentValidataResource(
        "foo.csv", irve_accent_valide_content
    ).extract_tabular_data()
    assert "accessibilité" in head


def test_detect_iso8859_1(irve_driveco_content):
    b_content = irve_driveco_content
    assert ValidataResource.detect_encoding(b_content) == "iso8859-1"


def test_read_iso8859_1(irve_driveco_content):
    head, rows = FileContentValidataResource(
        "foo.csv", irve_driveco_content
    ).extract_tabular_data()
    assert "accessibilité" in head, head


def test_ignore_bom(with_bom_content):
    head, rows = FileContentValidataResource(
        "with_bom.csv", with_bom_content
    ).extract_tabular_data()
    assert head
    assert head[0] == "id", head


def test_invalid_utf16(invalid_utf16_content):
    with pytest.raises(ValidataSourceError):
        FileContentValidataResource(
            "invalid_utf16.csv", invalid_utf16_content
        ).extract_tabular_data()
