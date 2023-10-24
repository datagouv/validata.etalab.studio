"""Application configuration."""
import logging
import os
from distutils.util import strtobool

from dotenv import load_dotenv

log = logging.getLogger(__name__)


def guess_bool(v):
    """Convert given value to boolean value."""
    return strtobool(v) if isinstance(v, str) else bool(v)


load_dotenv()


FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or None
if FLASK_SECRET_KEY is None:
    ERROR_MESSAGE = "FLASK_SECRET_KEY environment variable is not set, can't go further"
    log.error(ERROR_MESSAGE)
    raise ValueError(ERROR_MESSAGE)

SCRIPT_NAME = os.environ.get("SCRIPT_NAME") or ""


DEBUG_PYTHON_HTTP_CLIENT = guess_bool(os.environ.get("DEBUG_PYTHON_HTTP_CLIENT"))

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)

MATOMO_AUTH_TOKEN = os.getenv("MATOMO_AUTH_TOKEN") or None
MATOMO_BASE_URL = os.getenv("MATOMO_BASE_URL") or None
MATOMO_SITE_ID = os.getenv("MATOMO_SITE_ID") or None
if MATOMO_SITE_ID:
    MATOMO_SITE_ID = int(MATOMO_SITE_ID)
