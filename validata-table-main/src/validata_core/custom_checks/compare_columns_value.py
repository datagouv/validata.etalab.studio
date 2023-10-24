"""
    Compare columns value check

    Pour deux colonnes données, si les deux comportent une valeur, vérifie que
    la valeur de la première est :
    - supérieure (>)
    - supérieure ou égale (>=)
    - égale (==)
    - inférieure ou égale (<=)
    - inférieure (<)
    à la valeur de la deuxième colonne

    Si les deux valeurs sont numériques, c'est une comparaison numérique
        qui est utilisée.
    Si les deux valeurs ne sont pas numériques, c'est une comparaison lexicographique
        qui est utilisée.
    Si une valeur est numérique et l'autre lexicographique, une erreur est relevée.

    Paramètres :
    - column : le nom de la première colonne
    - column2 : le nom de la deuxième colonne
    - op : l'opérateur de comparaison (">", ">=", "==", "<=" ou "<")

    Messages d'erreur attendus :
    - Opérateur [??] invalide
    - La valeur de la colonne {col1} [{val1}] n'est pas comparable avec la valeur
        de la colonne {col2} [{val2}]
    - La valeur de la colonne {col1} [{val1}] devrait être {opérateur} à la valeur
        de la colonne {col2} [{val2}]

    Pierre Dittgen, Jailbreak
"""
import decimal

from frictionless import errors
from simpleeval import simple_eval

from .utils import build_check_error,  CustomCheckMultipleColumns

OP_LABELS = {
    ">": "supérieure",
    ">=": "supérieure ou égale",
    "==": "égale",
    "<=": "inférieure ou égale",
    "<": "inférieure",
}


class CompareColumnsValueError(errors.CellError):
    """Custom error."""

    code = "compare-columns-value"
    name = "Comparaison de colonnes"
    tags = ["#body"]
    template = "{note}."
    description = ""


class CompareColumnsValue(CustomCheckMultipleColumns):
    """Compare columns value check class."""

    code = "compare-columns-value"
    possible_Errors = [CompareColumnsValueError]

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__op = self.get("op")

    def _validate_start(self, all_columns):
        for col in all_columns:
            if col not in self.resource.schema.field_names:
                note = f"La colonne {col} n'est pas trouvée."
                yield build_check_error(CompareColumnsValue.code, note)
        if self.__op not in OP_LABELS:
            note = f"L'opérateur {self.__op!r} n'est pas géré."
            yield build_check_error(CompareColumnsValue.code, note)

    def _validate_row(self, cell_values, row):
        cell_value1 = cell_values[0]
        cell_value2 = cell_values[1]

        op = self.__op

        # Compare
        comparison_str = compute_comparison_str(cell_value1, op, cell_value2)
        if comparison_str is None:
            note = (
                f"La valeur de la colonne {self.get('column')} `{cell_value1}`"
                " n'est pas comparable avec la valeur de la colonne"
                f" {self.get('column2')} `{cell_value2}`."
            )
            yield CompareColumnsValueError.from_row(
                row, note=note, field_name=self.get('column')
            )
            return

        compare_result = simple_eval(comparison_str)

        if not compare_result:
            op_str = OP_LABELS[self.__op]
            note = (
                f"La valeur de la colonne {self.get('column')} `{cell_value1}` devrait"
                f" être {op_str} à la valeur de la colonne"
                f" {self.get('column2')} `{cell_value2}`."
            )
            yield CompareColumnsValueError.from_row(
                row, note=note, field_name=self.get('column')
            )

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column", "column2", "op"],
        "properties": {"column": {}, "column2": {}, "op": {"type": "string"}},
    }


def is_a_number(value):
    """Return True if value is a number (int or float)
    or a string representation of a number.
    """
    if type(value) in (int, float) or isinstance(value, decimal.Decimal):
        return True
    if not isinstance(value, str):
        return False
    if value.isnumeric():
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False


def compute_comparison_str(value1, op, value2):
    """ Computes comparison_str """

    # number vs number
    if is_a_number(value1) and is_a_number(value2):
        return f"{str(value1)} {op} {str(value2)}"

    # string vs string
    if isinstance(value1, str) and isinstance(value2, str):
        n_value1 = value1.replace('"', '\\"')
        n_value2 = value2.replace('"', '\\"')
        return f'"{n_value1}" {op} "{n_value2}"'

    # thing vs thing, compare string repr
    if type(value1) == type(value2):
        return f"'{value1}' {op} '{value2}'"

    # potato vs cabbage?
    return None
