"""Application route handlers."""

import logging
import urllib
from io import BytesIO

import cachetools
import requests
import validata_core
from flasgger import swag_from
from flask import request
from validata_core.helpers import (
    FileContentValidataResource,
    URLValidataResource,
    ValidataSourceError,
)

from validata_api.api import app, config
from validata_api.api.json_errors import abort_json, make_json_response

# Schema cache size (nb of simultaneously stored schemas)
SCHEMA_CACHE_SIZE = 20
# Schema time to live (in seconds)
SCHEMA_CACHE_TTL = 60


log = logging.getLogger(__name__)


def bytes_data(f):
    """Get bytes data from Werkzeug FileStorage instance."""
    iob = BytesIO()
    f.save(iob)
    iob.seek(0)
    return iob.getvalue()


@app.route("/")
def index():
    """Home."""
    apidocs_href = "{}/apidocs".format(config.SCRIPT_NAME)
    apidocs_url = urllib.parse.urljoin(request.url, apidocs_href)
    return make_json_response(
        {
            "apidocs_href": apidocs_href,
            "message": (
                "This is the home page of Validata Web API. "
                f"Its documentation is here: {apidocs_url}"
            ),
        },
        args=None,
    )


base_url = "https://gitlab.com/opendatafrance/scdl/deliberations"

specs_dict = {
    "get": {
        "summary": "Validate a tabular file from its URL",
        "parameters": [
            {
                "name": "schema",
                "in": "query",
                "type": "string",
                "format": "url",
                "description": "URL of schema to use for validation",
                "example": f"{base_url}/raw/master/schema.json",
                "required": True,
            },
            {
                "name": "url",
                "in": "query",
                "type": "string",
                "format": "url",
                "description": "URL of tabular file to validate",
                "example": f"{base_url}/raw/v2.0/examples/Deliberations_ok.csv",
                "required": True,
            },
            {
                "name": "header_case",
                "in": "query",
                "type": "boolean",
                "description": "Should validation of headers be case-sensitive",
                "default": "true",
                "required": False
            }
        ],
        "produces": ["application/json"],
    },
    "post": {
        "summary": "Validate an uploaded tabular file",
        "parameters": [
            {
                "name": "schema",
                "in": "formData",
                "type": "string",
                "format": "url",
                "description": "URL of schema to use for validation",
                "example": f"{base_url}/raw/master/schema.json",
                "required": True,
            },
            {
                "name": "file",
                "in": "formData",
                "type": "file",
                "description": "The file to upload",
                "required": True,
            },
            {
                "name": "header_case",
                "in": "formData",
                "type": "boolean",
                "descripton": "Should validation of headers be case-sensitive",
                "default": "true",
                "required": False
            }
        ],
        "consumes": ["multipart/form-data"],
        "produces": ["application/json"],
    },
    "responses": {
        "200": {
            "description": "Validation report",
            "schema": {"type": "object", "required": ["_meta", "schema", "report"]},
            "examples": [
                {
                    "_meta": {"version": "0.2.0"},
                    "schema": {},
                    "report": {
                        "error-count": 1,
                        "preset": "table",
                        "table-count": 1,
                        "tables": [
                            {
                                "error-count": 2,
                                "errors": [
                                    {
                                        "code": "invalid-column-delimiter",
                                        "column-number": None,
                                        "message": None,
                                        "message-data": {
                                            "detected": ";",
                                            "expected": ",",
                                        },
                                        "row-number": None,
                                    },
                                    {
                                        "code": "compare-columns-value",
                                        "column-number": 11,
                                        "message": (
                                            "La valeur de la colonne PREF_DATE"
                                            " [2017-02-03] devrait être supérieure "
                                            "ou égale à la valeur de la colonne"
                                            " DELIB_DATE [2017-10-15]"
                                        ),
                                        "message-data": {
                                            "column1": "PREF_DATE",
                                            "column2": "DELIB_DATE",
                                            "op": "supérieure ou égale",
                                            "value1": "2017-02-03",
                                            "value2": "2017-10-15",
                                        },
                                        "row-number": 2,
                                    },
                                ],
                                "format": "inline",
                                "headers": [
                                    "COLL_NOM",
                                    "COLL_SIRET",
                                    "DELIB_ID",
                                    "DELIB_DATE",
                                    "DELIB_MATIERE_CODE",
                                    "DELIB_MATIERE_NOM",
                                    "DELIB_OBJET",
                                    "BUDGET_ANNEE",
                                    "BUDGET_NOM",
                                    "PREF_ID",
                                    "PREF_DATE",
                                    "VOTE_EFFECTIF",
                                    "VOTE_REEL",
                                    "VOTE_POUR",
                                    "VOTE_CONTRE",
                                    "VOTE_ABSTENTION",
                                    "DELIB_URL",
                                ],
                                "row-count": 2,
                                "schema": "table-schema",
                                "source": "inline",
                                "time": 0.006,
                                "valid": False,
                            }
                        ],
                        "time": 0.014,
                        "valid": False,
                        "warnings": [],
                    },
                }
            ],
        },
        "400": {
            "description": "Error",
            "schema": {"type": "object", "required": ["_meta", "message"]},
            "examples": [
                {"_meta": {"version": "0.2.0"}, "message": "Unsupported format error"}
            ],
        },
    },
}


@cachetools.cached(cachetools.TTLCache(SCHEMA_CACHE_SIZE, SCHEMA_CACHE_TTL))
def download_schema(schema_url):
    """Download schema by its given url"""
    return requests.get(schema_url).json()


@app.route("/validate", methods={"GET", "POST"})
@swag_from(specs_dict)
def validate():
    """Validate endpoint."""

    if request.method == "GET":
        args = {
            "schema": request.args.get("schema"),
            "url": request.args.get("url"),
            "header_case": request.args.get("header_case")
        }
    else:
        assert request.method == "POST", request.method
        args = {
            "schema": request.form.get("schema"),
            "header_case": request.form.get("header_case")
        }

    if not args["schema"]:
        abort_json(400, args, 'Missing or empty "schema" parameter')

    # Download Schema from URL to get control on cache
    # schema json dict is passed to validate function as a dict
    try:
        schema_dict = download_schema(args["schema"])
    except Exception as err:
        abort_json(400, {}, str(err))

    validata_resource = None

    if request.method == "GET":
        # URL validation
        if not args["url"]:
            abort_json(400, args, 'Missing or empty "url" parameter')
        validata_resource = URLValidataResource(args["url"])

    elif request.method == "POST":
        # Uploaded file validation
        f = request.files.get("file")
        if f is None:
            abort_json(400, args, 'Missing or empty "file" parameter')
        validata_resource = FileContentValidataResource(f.filename, bytes_data(f))

    try:
        header, rows = validata_resource.extract_tabular_data()
    except ValidataSourceError as err:
        body = {
            "error": {
                "name": err.name,
                "message": err.message,
            }
        }
        return make_json_response(body, args)

    if args['header_case'] is None:
        header_case = True
    else:
        header_case = args['header_case'].lower() == 'true'
    validation_report = validata_core.validate([header] + rows, schema_dict, header_case)

    body = {
        "report": validation_report.to_dict(),
    }

    return make_json_response(body, args)
