# -*- coding: utf-8 -*-
"""
    Cohesive columns value check

    Vérifie que pour une liste de colonnes donnée, toutes les colonnes ont une valeur
    ou aucune des colonnes n'a une valeur

    Paramètres :
    - column : la première colonne
    - othercolumns : les autres colonnes qui doivent être remplies (ou non)

    Messages d'erreur attendus :
    - Colonne(s) non trouvée(s) : {liste de noms de colonnes non trouvées}
    - Les colonnes {liste des noms de colonnes} doivent toutes comporter une valeur
    ou toutes être vides

    Pierre Dittgen, Jailbreak
"""
from frictionless import errors

from .utils import build_check_error, CustomCheckMultipleColumns

# Module API


class CohesiveColumnsValueError(errors.CellError):
    """Custom error."""

    code = "cohesive-columns-value"
    name = "Cohérence entre colonnes"
    tags = ["#body"]
    template = "incohérence relevée ({note})."
    description = ""


class CohesiveColumnsValue(CustomCheckMultipleColumns):
    """
    Cohesive columns value check class
    """

    code = "cohesive-columns-value"
    possible_Errors = [CohesiveColumnsValueError]

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")
        self.__other_columns = self.get("othercolumns")
        self.__all_columns = [self.__column] + self.__other_columns
        self.__columns_nb = len(self.__all_columns)
        self.__skip_empty_cells = False

    def _validate_start(self, all_columns):
        if self.__column not in self.resource.schema.field_names:
            note = f"La colonne {self.__column!r} est manquante."
            yield build_check_error(CohesiveColumnsValue.code, note)
        elif len(self.__other_columns) == 0:
            note = "La liste de colonnes à comparer est vide"
            yield build_check_error(CohesiveColumnsValue.code, note)
        else:
            for col in self.__other_columns:
                if col not in self.resource.schema.field_names:
                    note = f"La colonne à comparer {col!r} est manquante"
                    yield build_check_error(CohesiveColumnsValue.code, note)

    def validate_row(self, row):
        cell_value = row[self.__column]

        status = valued(cell_value)
        other_cell_values = [row[col] for col in self.__other_columns]

        # test if all columns are valued or all columns are empty
        if any(valued(v) != status for v in other_cell_values):
            columns_str = ", ".join(self.__all_columns)
            note = (
                f"Les colonnes {columns_str} doivent toutes comporter une valeur"
                " ou toutes être vides"
            )
            yield CohesiveColumnsValueError.from_row(
                row, note=note, field_name=self.__column
            )

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column", "othercolumns"],
        "properties": {"column": {"type": "string"}, "othercolumns": {"type": "array"}},
    }


def valued(val):
    return val is not None and val != ""
