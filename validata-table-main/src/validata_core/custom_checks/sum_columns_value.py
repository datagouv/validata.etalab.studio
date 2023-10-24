import decimal
import re

from frictionless import errors

from .utils import build_check_error, CustomCheckMultipleColumns

"""
    Sum columns value check

    Pour une colonne donnée (column) et une liste de colonnes (columns),
    on vérifie que la première colonne contient bien
    la somme des valeurs entières des autres colonnes

    La vérification ne s'effectue pas si l'ensemble des colonnes est vide

    Paramètres :
    - column : le nom de la première colonne contenant la somme
    - columns : le nom des colonnes contenant les valeurs à ajouter

    Messages d'erreur attendus :
    - La valeur de la colonne {col} [val] n'est pas entière, il n'est pas possible
        de vérifier que {col} = {col1} + {col2} + ...
    - La valeur des colonnes {col1}, {col2}, ... ne sont pas entières,
        il n'est pas possible de vérifier que {col} = {col1} + {col2} + ...
    - La somme des valeurs des colonnes {col1}, {col2}, ... est {sum},
        ce nombre est différent de celui attendu dans {col} [val]

    Pierre Dittgen, Jailbreak
"""

# Module API

INT_RE = re.compile(r"^\d+$")


class SumColumnsValueError(errors.CellError):
    """Custom error."""

    code = "sum-columns-value"
    name = "Somme de colonnes"
    tags = ["#body"]
    template = "La somme de colonne ne peut être calculée ({note})."
    description = "Somme de colonnes"


class SumColumnsValue(CustomCheckMultipleColumns):
    """Sum columns value check."""

    code = "sum-columns-value"
    possible_Errors = [SumColumnsValueError]

    def _validate_start(self, all_columns):
        for col in all_columns:
            if col not in self.resource.schema.field_names:
                note = f"la colonne {col} n'est pas trouvée"
                yield build_check_error(SumColumnsValue.code, note)
        if len(self.get("columns")) < 2:
            note = "le nombre de colonnes est insuffisant pour l'addition"
            yield build_check_error(SumColumnsValue.code, note)

    def _validate_row(self, cell_values, row):

        # Checks that all values are integer
        # => already checked by schema

        # Check sum
        computed_sum = sum(int(row[col]) for col in self.get("columns"))
        column_sum = int(row[self.get("column")])
        if computed_sum != column_sum:
            column = self.get("column")
            column_value_list = ", ".join(
                f"{col} ({int(row[col])})" for col in self.get("columns")
            )
            note = (
                f"la somme des valeurs des colonnes {column_value_list!r} est"
                f" `{computed_sum}`, ce nombre est différent de celui trouvé"
                f" dans la colonne {column!r} (`{column_sum}`)"
            )
            yield SumColumnsValueError.from_row(row, note=note, field_name=column)

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column", "columns"],
        "properties": {"column": {"type": "string"}, "columns": {"type": "array"}},
    }


def valued(val):
    """ Return True if the given string value is not empty """
    return val != "" and val is not None


def is_int(value):
    """ Return True if the given string contains an integer """
    if isinstance(value, int) or isinstance(value, decimal.Decimal):
        return True
    if isinstance(value, str):
        return INT_RE.match(value)
    return False
