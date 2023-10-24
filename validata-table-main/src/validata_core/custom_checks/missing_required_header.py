"""Reimplementation of NonMatchingHeader check,
   taking into account missing header, extra header and wrong header order."""
from frictionless import Check, errors
from validata_core import helpers

class MissingRequiredHeaderError(errors.HeaderError):
    """Custom error."""

    code = "missing-required-header"
    name = "Colonne obligatoire manquante"
    tags = ["#head", "#structure"]
    template = "{note}"
    description = ""


class MissingRequiredHeader(Check):
    """Custom check."""

    possible_Errors = [MissingRequiredHeaderError]

    def __init__(self, descriptor=None):
        """
        schema required fields are provided as task parameter
        We can't use self.resource.schema to access to the whole schema as
        `schema_sync=True` removes schema fields that don't appear in table.
        """
        super().__init__(descriptor)
        self.__required_field_names = self.get("required_field_names")

    def validate_start(self):

        for pos, field_name in enumerate(self.__required_field_names):
            missing_required_header_error = False
            if self.resource.header._Header__ignore_case:
                lower_field_name = field_name.lower()
                lower_resource_header = helpers.to_lower(self.resource.header)
                if lower_field_name not in lower_resource_header:
                    missing_required_header_error = True
            elif field_name not in self.resource.header:
                missing_required_header_error = True

            if missing_required_header_error:
                yield MissingRequiredHeaderError(
                    note=f"La colonne obligatoire `{field_name}` est manquante.",
                    labels=self.resource.header,
                    row_positions=[pos],
                )

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["required_field_names"],
        "properties": {"required_field_names": {"type": "array"}},
    }
