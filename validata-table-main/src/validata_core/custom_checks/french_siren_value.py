import stdnum.fr.siren
from frictionless import errors

from .utils import CustomCheckSingleColumn


class FrenchSirenValueError(errors.CellError):
    """Custom error."""

    code = "french-siren-value"
    name = "Numéro SIREN invalide"
    tags = ["#body"]
    template = "La valeur {cell} n'est pas un numéro SIREN français valide."
    description = (
        "Le numéro de SIREN indiqué n'est pas valide selon la définition"
        " de l'[INSEE](https://www.insee.fr/fr/metadonnees/definition/c2047)."
    )


class FrenchSirenValue(CustomCheckSingleColumn):
    """Check french SIREN number validity."""

    code = "french-siren-value"
    possible_Errors = [FrenchSirenValueError]  # type: ignore

    def _validate_start(self):
        yield from []

    def _validate_row(self, cell_value, row):
        if not stdnum.fr.siren.is_valid(cell_value):
            yield FrenchSirenValueError.from_row(row, note="", field_name=self.get('column'))

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }
