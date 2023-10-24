import opening_hours
from frictionless import errors

from .utils import CustomCheckSingleColumn


class OpeningHoursValueError(errors.CellError):
    """Custom error."""

    code = "opening-hours-value"
    name = "Horaires d'ouverture incorrects"
    tags = ["#body"]
    template = (
        "La valeur '{cell}' n'est pas une définition d'horaire d'ouverture correcte.\n\n"
        " Celle-ci doit respecter la spécification"
        " [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Key:opening_hours)"
        " de description d'horaires d'ouverture."
    )
    description = ""


class OpeningHoursValue(CustomCheckSingleColumn):
    """Check opening hours validity."""

    code = "opening-hours-value"
    possible_Errors = [OpeningHoursValueError]  # type: ignore

    def _validate_start(self):
        yield from []

    def _validate_row(self, cell_value, row):
        if not opening_hours.validate(cell_value):
            yield OpeningHoursValueError.from_row(row, note="", field_name=self.get('column'))

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }
