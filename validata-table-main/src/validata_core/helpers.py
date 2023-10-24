import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union, List

import frictionless
from frictionless.plugins.excel import ExcelDialect

from .error_messages import error_translate

log = logging.Logger(__name__)


@dataclass
class ValidataSourceError(Exception):
    name: str
    message: str


class ValidataResource(ABC):
    """A resource to validate: url or uploaded file"""

    @abstractmethod
    def build_table_args(self):
        """return (source, option_dict)"""
        pass

    @abstractmethod
    def get_source(self):
        """return filename or URL"""
        pass

    def extract_tabular_data(self):
        """Extract header and data rows from source."""
        table_source, table_options = self.build_table_args()
        return _extract_header_and_rows_from_frictionless_source(
            table_source, **table_options
        )

    def _dialect_option(self, format: str) -> dict:
        return (
            {"dialect": ExcelDialect(preserve_formatting=True)}
            if format == "xlsx"
            else {}
        )

    @classmethod
    def detect_encoding(cls, bytes_data):
        """Try to decode using utf-8 first, fallback on frictionless helper function."""
        try:
            bytes_data.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            encoding = frictionless.Detector().detect_encoding(bytes_data)
            return encoding.lower() if encoding else None


class URLValidataResource(ValidataResource):
    """URL resource"""

    def __init__(self, url):
        """Built from URL"""
        self.url = url

    def get_source(self):
        return self.url

    def build_table_args(self):
        """URL implementation"""
        suffix = Path(self.url).suffix
        format = suffix[1:] if suffix.startswith(".") else ""

        return (
            self.url,
            {
                "detector": frictionless.Detector(
                    encoding_function=ValidataResource.detect_encoding
                ),
                **self._dialect_option(format),
            },
        )


class FileContentValidataResource(ValidataResource):
    """Uploaded file resource"""

    def __init__(self, filename: str, content: bytes):
        """Built from filename and bytes content"""
        self.filename = filename
        self.file_ext = Path(filename).suffix.lower()
        self.content = content

    def get_source(self):
        return self.filename

    def build_table_args(self):
        """Uploaded file implementation"""

        def detect_format_from_file_extension(file_ext: str):
            if file_ext in (".csv", ".tsv", ".ods", ".xls", ".xlsx"):
                return file_ext[1:]
            return None

        format = detect_format_from_file_extension(self.file_ext)
        options = {
            "format": format,
            "detector": frictionless.Detector(
                encoding_function=ValidataResource.detect_encoding
            ),
            **self._dialect_option(format),
        }
        if format in {"csv", "tsv"}:
            options["encoding"] = ValidataResource.detect_encoding(self.content)
        source = self.content

        return (source, options)


def _extract_header_and_rows_from_frictionless_source(source, **source_options):
    """Extract header and data rows from frictionless source and options."""
    try:
        with frictionless.Resource(source, **source_options) as res:
            if res.list_stream is None:
                raise ValueError("impossible de lire le contenu")
            lines = list(res.read_lists())
            if not lines:
                raise ValueError("contenu vide")
            header, rows = lines[0], lines[1:]
            # Fix BOM issue on first field name
            BOM_UTF8 = "\ufeff"
            if header and header[0].startswith(BOM_UTF8):
                header = [header[0].replace(BOM_UTF8, "")] + header[1:]
            return header, rows
    except ValueError as vex:
        raise ValidataSourceError(
            name="source-error",
            message=vex.args[0],
        ) from vex
    except frictionless.exception.FrictionlessException as exc:
        log.exception(
            "Exception while reading source %r with options: %r", source, source_options
        )
        validata_error = error_translate(exc.error)
        raise ValidataSourceError(
            name=validata_error.name,
            message=validata_error.message,
        ) from exc


BODY_TAGS = frozenset(["#body", "#cell", "#content", "#row", "#table"])
STRUCTURE_TAGS = frozenset(["#head", "#structure"])


def is_body_error(err: Union[frictionless.errors.Error, Dict]) -> bool:
    """Classify the given error as 'body error' according to its tags."""
    tags = err.tags if isinstance(err, frictionless.errors.Error) else err["tags"]
    return bool(BODY_TAGS & set(tags))


def is_structure_error(err: Union[frictionless.errors.Error, Dict]) -> bool:
    """Classify the given error as 'structure error' according to its tags."""
    tags = err.tags if isinstance(err, frictionless.errors.Error) else err["tags"]
    return bool(STRUCTURE_TAGS & set(tags))


def to_lower(str_array: List[str]) -> List[str]:
    """Lower all the strings in a list"""
    return [s.lower() for s in str_array]

