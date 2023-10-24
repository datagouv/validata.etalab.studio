import stdnum.fr.siret
from frictionless import errors

from .utils import CustomCheckSingleColumn


class FrenchSiretValueError(errors.CellError):
    """Custom error."""

    code = "french-siret-value"
    name = "Numéro SIRET invalide"
    tags = ["#body"]
    template = "La valeur {cell} n'est pas un numéro SIRET français valide."
    description = (
        "Le numéro de SIRET indiqué n'est pas valide selon la définition"
        " de l'[INSEE](https://www.insee.fr/fr/metadonnees/definition/c1841)."
    )


class FrenchSiretValue(CustomCheckSingleColumn):
    """Check french SIRET number validity."""

    code = "french-siret-value"
    possible_Errors = [FrenchSiretValueError]  # type: ignore

    def _validate_start(self):
        yield from []

    def _validate_row(self, cell_value, row):
        if not stdnum.fr.siret.is_valid(cell_value):
            yield FrenchSiretValueError.from_row(row, note="", field_name=self.get('column'))

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }
