"""Respond JSON errors instead of HTML. Useful for HTTP/JSON APIs."""

# From https://coderwall.com/p/xq88zg/json-exception-handler-for-flask

import logging

import importlib_metadata
import ujson as json
from flask import Response, abort
from toolz import assoc
from werkzeug.exceptions import HTTPException, default_exceptions

log = logging.getLogger(__name__)


def abort_json(status_code, args, message=None):
    if message is None:
        exc = default_exceptions.get(status_code)
        if exc is not None:
            message = exc.description
    response = make_json_response({"message": message}, args, status_code=status_code)
    if status_code == 500:
        log.error((message, args, status_code))
    abort(response)


def error_handler(error):
    status_code = error.code if isinstance(error, HTTPException) else 500
    message = (
        str(error) if isinstance(error, HTTPException) else "Internal server error"
    )
    return make_json_response({"message": message}, args=None, status_code=status_code)


def get_version():
    try:
        version = importlib_metadata.version('validata-table')
    except importlib_metadata.PackageNotFoundError:
        version = "Numéro de version uniquement disponible si le package " \
                  "validata-table est installé"
    return version


def make_json_response(data, args, status_code=None):
    meta = {
        "validata-table-version": get_version(),
    }
    if args:
        meta = assoc(meta, "args", args)
    return Response(
        json.dumps(assoc(data, "_meta", meta), sort_keys=True),
        mimetype="application/json",
        status=status_code,
    )


class JsonErrors:
    """
    Respond JSON errors.
    Register error handlers for all HTTP exceptions.

    Special case: when FLASK_DEBUG=1 render HTTP 500 errors as HTML instead of JSON.
    """

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.register(HTTPException)
        for code in default_exceptions:
            self.register(code)

    def register(self, exception_or_code, handler=None):
        self.app.errorhandler(exception_or_code)(handler or error_handler)
