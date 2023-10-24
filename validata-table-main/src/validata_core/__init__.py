import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

import frictionless

from validata_core.custom_checks.utils import build_check_error

from .custom_checks import MissingRequiredHeader, available_checks
from .error_messages import error_translate
from .helpers import (
    _extract_header_and_rows_from_frictionless_source,
    is_body_error,
    is_structure_error,
)
from .structure_warnings import iter_structure_warnings

log = logging.getLogger(__name__)

VALIDATA_MAX_ROWS = 100000


def extract_required_field_names(schema: frictionless.schema.Schema):
    return [
        field["name"]
        for field in schema.get("fields", [])
        if field.get("constraints") and field["constraints"].get("required", False)
    ]


def compute_badge_metrics(report, config) -> Optional[dict]:
    """Compute badge metrics from report statistics and badge configuration."""

    def build_badge(structure_status, body_status=None, error_ratio=None):
        """Badge info creation"""
        if structure_status == "KO":
            return {"structure": "KO"}
        return {
            "structure": structure_status,
            "body": body_status,
            "error-ratio": error_ratio,
        }

    if not report["tasks"]:
        return None

    table_report = report["tasks"][0]

    # Compute number of cells
    resource_data = table_report["resource"]["data"]
    cell_total_number = len(resource_data[0]) * len(resource_data)

    # No errors
    if (
        table_report["stats"]["errors"] == 0
        and len(table_report["structure_warnings"]) == 0
    ):
        return build_badge("OK", "OK", 0.0)

    # Structure part
    structure_status = None
    structure_errors_count = len(
        [err for err in table_report["errors"] if is_structure_error(err)]
    )
    if structure_errors_count == 0:
        structure_status = (
            "OK" if len(table_report["structure_warnings"]) == 0 else "WARN"
        )
    else:
        return build_badge("KO")

    # body part
    value_errors = [err for err in table_report["errors"] if is_body_error(err)]
    if len(value_errors) == 0:
        return build_badge(structure_status, "OK", 0.0)

    # Computes error ratio
    weight_dict = config["body"]["errors-weight"]
    err_code_counter = Counter([err.code for err in value_errors])
    ratio = (
        sum(
            [
                nb * weight_dict.get(err_code, 1.0)
                for err_code, nb in err_code_counter.items()
            ]
        )
        / cell_total_number
    )
    body_status = "WARN" if ratio < config["body"]["acceptability-threshold"] else "KO"

    return build_badge(structure_status, body_status, ratio)


def validate(source, schema, header_case=True, **options):
    """
    Validate a `source` using a `schema`.
    :param source: data source to validate
    :param schema: schema used for validation
    :param header_case: by default, header validation is case-sensitive
    :return: report of validation
    """

    # Handle different schema format
    if isinstance(schema, dict) or (
        isinstance(schema, str) and schema.startswith("http")
    ):
        schema = frictionless.schema.Schema(schema)
    elif not isinstance(schema, frictionless.schema.Schema):
        schema = frictionless.schema.Schema(str(schema))

    # First extra check is devoted to detect required missing headers
    required_field_names = extract_required_field_names(schema)
    extra_checks = [
        MissingRequiredHeader({"required_field_names": required_field_names})
    ]

    # Dynamically add custom check based on schema needs
    check_errors = []
    for cc_conf in schema.get("custom_checks", []):
        cc_name = cc_conf["name"]
        if cc_name not in available_checks:
            check_errors.append(
                build_check_error(cc_name, note="custom check inconnu.")
            )
            continue
        cc_class = available_checks[cc_name]
        cc_descriptor = cc_conf["params"]
        extra_checks.append(cc_class(cc_descriptor))

    # Merge options to pass to frictionless
    validate_options = {
        "layout": frictionless.Layout(limit_rows=VALIDATA_MAX_ROWS, header_case=header_case),
        "checks": extra_checks,  # add custom_checks if needed
        # Don't care about missing, extra or unordered columns
        "detector": frictionless.Detector(schema_sync=True),
        **{
            k: v
            for k, v in options.items()
            if k
            in {
                "format",
                "infer_schema",
                "infer_fields",
                "limit_errors",
                "pick_errors",
                "query",
                "skip_errors",
                "scheme",
                "table_limit",
            }
        },
    }
    original_schema = schema.copy()
    report = frictionless.validate_resource(source, schema=schema, **validate_options)

    # add structure warnings if needed
    source_options = {
        k: v
        for k, v in validate_options.items()
        if k in {"dialect", "encoding", "format", "scheme"}
    }

    source_header = None
    if report["tasks"]:
        source_header, _ = _extract_header_and_rows_from_frictionless_source(
            source, **source_options
        )
    for table in report["tasks"]:
        table["structure_warnings"] = list(
            iter_structure_warnings(
                source_header, required_field_names, original_schema, header_case
            )
        )
        if check_errors:
            table["errors"].extend(check_errors)
            report['stats']['errors'] += len(check_errors)
            report["valid"] = False

    # translate errors
    report["errors"] = [error_translate(err, schema) for err in report["errors"]]
    for table in report["tasks"]:
        table["errors"] = [error_translate(err, schema) for err in table["errors"]]

    # Add date
    report["date"] = datetime.now(timezone.utc).isoformat()

    return report


def compute_badge(report, config) -> dict:
    """Compute badge from report statistics and badge configuration."""

    def build_badge(structure_status, body_status=None, error_ratio=None):
        """Badge info creation"""
        if structure_status == "KO":
            return {"structure": "KO"}
        return {
            "structure": structure_status,
            "body": body_status,
            "error-ratio": error_ratio,
        }

    # Gets stats from report
    stats = report["tables"][0]["error-stats"]

    # And total number of cells
    column_count = len(report["tables"][0]["headers"])
    row_count = report["tables"][0]["row-count"]
    cell_total_number = column_count * row_count

    # No errors
    if stats["count"] == 0:
        return build_badge("OK", "OK", 0.0)

    # Structure part
    structure_status = None
    if stats["structure-errors"]["count"] == 0:
        structure_status = "OK"
    else:
        cbc = stats["structure-errors"]["count-by-code"]
        if len(cbc) == 1 and "invalid-column-delimiter" in cbc:
            structure_status = "WARN"
        else:
            # structure_status = 'KO'
            return build_badge("KO")

    # body part
    value_errors = stats["value-errors"]
    if value_errors["count"] == 0:
        return build_badge(structure_status, "OK", 0.0)

    # Computes error ratio
    weight_dict = config["body"]["errors-weight"]
    ratio = (
        sum(
            [
                nb * weight_dict.get(err, 1.0)
                for err, nb in value_errors["count-by-code"].items()
            ]
        )
        / cell_total_number
    )
    body_status = "WARN" if ratio < config["body"]["acceptability-threshold"] else "KO"

    return build_badge(structure_status, body_status, ratio)
