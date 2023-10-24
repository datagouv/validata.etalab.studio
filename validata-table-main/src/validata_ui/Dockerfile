FROM python:3.9-slim-bullseye as python-base
LABEL maintainer="admin@multi.coop"

ENV \
    # ------- PYTHON ------- #
    # prevents buffer input/output operations, displaying prints and log messages immediately
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # -------- PIP --------- #
    # do not keep dependencies downloaded by "pip install"
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # ------- POETRY ------- #
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.6.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # ------- PATHS ------- #
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/validata-table" \
    VENV_PATH="/opt/validata-table/.venv" \
    # This needs to be a volume were the code lives
    SRC_PATH="/opt/validata-table/src"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# ---------------------------
# `builder-base` stage is used to build deps + create our virtual environment
#  using poetry
# ---------------------------

FROM python-base as builder-base

# deps for installing poetry and deps for building python deps
RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3.9 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH

# Copy project code
COPY ../../ ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --without dev

# ---------------------------
# `development` image is used during development / testing
# ---------------------------

FROM python-base as development

# copy poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH

# install dev dependencies
RUN poetry install

WORKDIR $SRC_PATH

EXPOSE 5000

# Number of workers is defined by `WEB_CONCURRENCY` env variable.
# Cf https://docs.gunicorn.org/en/stable/settings.html#workers
 CMD exec gunicorn --bind 0.0.0.0:5000 --timeout 60 --reload validata_ui.app:app

## ---------------------------
## `pre-production` image is used in production
## ---------------------------

FROM python-base as preproduction

EXPOSE 5000

# copy from builder-base the virutal environment venv
COPY --from=builder-base $SRC_PATH/validata_core $SRC_PATH/validata_core
COPY --from=builder-base $SRC_PATH/validata_api $SRC_PATH/validata_api
COPY --from=builder-base $SRC_PATH/validata_ui $SRC_PATH/validata_ui
COPY --from=builder-base $VENV_PATH $VENV_PATH

# Add nginx config file
ADD nginx.conf.sigil $PYSETUP_PATH

WORKDIR $SRC_PATH

# Number of workers is defined by `WEB_CONCURRENCY` env variable.
# Cf https://docs.gunicorn.org/en/stable/settings.html#workers
CMD exec gunicorn --bind 0.0.0.0:5000 --timeout 60 --workers 4 validata_ui.app:app



## ---------------------------
## `production` image is used in production
## ---------------------------

FROM python-base as production

EXPOSE 5000

# copy from builder-base the virutal environment venv
COPY --from=builder-base $SRC_PATH/validata_core $SRC_PATH/validata_core
COPY --from=builder-base $SRC_PATH/validata_api $SRC_PATH/validata_api
COPY --from=builder-base $SRC_PATH/validata_ui $SRC_PATH/validata_ui
COPY --from=builder-base $VENV_PATH $VENV_PATH

# Add nginx config file
ADD nginx.conf.sigil $PYSETUP_PATH

WORKDIR $SRC_PATH

# Number of workers is defined by `WEB_CONCURRENCY` env variable.
# Cf https://docs.gunicorn.org/en/stable/settings.html#workers
CMD exec gunicorn --bind 0.0.0.0:5000 --timeout 60 --workers 4 validata_ui.app:app
