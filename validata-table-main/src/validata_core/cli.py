#!/usr/bin/env python3

"""Validate tabular file (CSV, XLS, etc.) against a table schema and custom validators,
and adding pre-checks which can fix automatically some errors to reach the real checks.
"""

import argparse
import json
import logging
import sys

from . import validate


def cli():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "source", help="URL or path to tabular file (CSV, XLS, etc.) to validate"
    )
    parser.add_argument("--log", default="WARNING", help="level of logging messages")
    parser.add_argument("--schema", help="URL or path to table schema JSON file")
    parser.add_argument("--ignore_header_case", action='store_false', help="Cancel header case sensitivity",
                        required=False)
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(
        format="%(levelname)s:%(name)s:%(message)s",
        level=numeric_level,
        stream=sys.stderr,  # script outputs data
    )

    report = validate(args.source, args.schema, args.ignore_header_case)

    json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)

    return 0
