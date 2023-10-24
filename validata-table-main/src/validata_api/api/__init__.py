"""Application definition."""


import http.client
import logging

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from validata_api.api import config
from validata_api.api.json_errors import JsonErrors, get_version

log = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

if config.DEBUG_PYTHON_HTTP_CLIENT:
    http.client.HTTPConnection.debuglevel = 1  # type: ignore

# Set Werkzeug's `strict_slashes` option for all routes
# instead of defining it for each route individually.
# From https://stackoverflow.com/a/33285603
app.url_map.strict_slashes = False

JsonErrors(app)

CORS(app)

matomo = None
if config.MATOMO_AUTH_TOKEN and config.MATOMO_BASE_URL and config.MATOMO_SITE_ID:
    from flask_matomo import Matomo

    matomo = Matomo(
        app,
        matomo_url=config.MATOMO_BASE_URL,
        id_site=config.MATOMO_SITE_ID,
        token_auth=config.MATOMO_AUTH_TOKEN,
    )


app.config["SWAGGER"] = {
    "title": "Validata API",
    "description": (
        "This is the documentation of "
        "[Validata Web API](https://gitlab.com/validata-table/validata-api). "
        "Each endpoint is listed below, and if you click on it you will see "
        "its parameters. "
        "It's also possible to try these endpoints directly from this page "
        "by setting parameters values in a web form."
    ),
    "basePath": config.SCRIPT_NAME,
    "version": get_version(),
    "uiversion": 3,
    "termsOfService": None,  # TODO Set url once terms-of-service page will be created.
}
Swagger(app)


# Keep this import after app initialisation (to avoid cyclic imports)
from validata_api.api import route_handlers  # noqa isort:skip
