import json

import pytest
from validata_core import validate


@pytest.fixture
def schema_coordinates():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "coordonneesXY",
                "title": "Coordonnees GPS (longitude, latitude)",
                "type": "geopoint",
            },
        ],
        "custom_checks": [
            {"name": "french-gps-coordinates", "params": {"column": "coordonneesXY"}}
        ],
    }


@pytest.fixture
def schema_coordinates_array():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "coordonneesXY",
                "title": "Coordonnees GPS (longitude, latitude)",
                "type": "geopoint",
                "format": "array",
            },
        ],
        "custom_checks": [
            {"name": "french-gps-coordinates", "params": {"column": "coordonneesXY"}}
        ],
    }


def test_reversed_coordinates(schema_coordinates):
    source = [["coordonneesXY"], ["48.85837, 2.294481"]]
    report = validate(source, schema_coordinates)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "reversed-french-gps-coordinates"


def test_non_french_coordinates(schema_coordinates):
    source = [["coordonneesXY"], ["48.85837, 52.0"]]
    report = validate(source, schema_coordinates)
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "french-gps-coordinates"


def test_french_coordinates(schema_coordinates):
    source = [["coordonneesXY"], ["2.294481, 48.85837"]]
    report = validate(source, schema_coordinates)
    assert report.valid


def test_french_coordinates_as_array(schema_coordinates_array):
    source = [["coordonneesXY"], ["[2.294481, 48.85837]"]]
    report = validate(source, schema_coordinates_array)
    assert report.valid


@pytest.fixture
def schema_coordinates_for_none_value():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {
                "name": "coordonneesXY",
                "title": "Coordonnees GPS (longitude, latitude)",
                "type": "geopoint",
            },
        ],
        "custom_checks": [
            {"name": "french-gps-coordinates", "params": {"column": "coordonneesXY"}}
        ],
    }


# To succeed this test, the resource tested needs to have at least one value in row containing None values,
# otherwise, an error 'blank-row' occurs from frictionless and appears in the validation report.
def test_do_not_apply_french_gps_coordindates_on_missing_values_on_optional_field(schema_coordinates_for_none_value):
    source = [["A", "coordonneesXY"], ["a", "2.294481, 48.85837"], ["a", None]]
    report = validate(source, schema_coordinates_for_none_value)
    assert report.valid


@pytest.fixture
def schema_coordinates_on_required_field():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "title": "Field A", "type": "string", "constraints": {"required": True}},
            {
                "name": "coordonneesXY",
                "title": "Coordonnees GPS (longitude, latitude)",
                "type": "geopoint",
                "constraints": {"required": True},
            },
        ],
        "custom_checks": [
            {"name": "french-gps-coordinates", "params": {"column": "coordonneesXY"}}
        ],
    }


# To succeed this test, the resource tested needs to have at least one value in row containing None values,
# otherwise, an error 'blank-row' occurs from frictionless and appears in the validation report.
def test_french_gps_coordindates_on_missing_values_when_required_field(schema_coordinates_on_required_field):
    source = [["A", "coordonneesXY"], ["a", "2.294481, 48.85837"], ["a", None]]
    report = validate(source, schema_coordinates_on_required_field)
    print(report)
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "constraint-error"
    assert report["tasks"][0]["errors"][0]["name"] == "Cellule vide"
