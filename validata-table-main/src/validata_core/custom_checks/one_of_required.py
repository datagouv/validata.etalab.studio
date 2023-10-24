# -*- coding: utf-8 -*-
"""
    One of required check

    Ce custom check vérifie :
    - Pour les deux colonnes relatives à ce custom check, pour une ligne donnée, au moins une des deux colonnes doit
    contenir une valeur,
    - Pour une ligne donnée, les deux colonnes peuvent contenir chacune une valeur,
    - Si une des deux colonnes est manquantes, alors toute valeur manquante dans l'autre colonne engendre une erreur de
    validation,
    - Si les deux colonnes sont manquantes cela engendre une erreur de validation.


    Paramètres :
    - column1 : la première colonne
    - column2 : la deuxième colonne

    Messages d'erreur attendus :
    - Les colonnes {nom de la première colonne} et {nom de la deuxième colonne} sont manquantes.
    - Au moins l'une des colonnes {liste des noms de colonnes} doit comporter une valeur.

    Amélie Rondot, multi
"""

from frictionless import Check, errors
from .utils import build_check_error, valued, CustomCheckMultipleColumns

# Module API


class OneOfRequiredError(errors.RowError):
    """Custom error."""

    code = "one-of-required"
    name = "Une des deux colonnes requises"
    tags = ["#body"]
    template = "incohérence relevée ({note})."
    description = ""


class OneOfRequiredErrorMissingBothColumns(errors.TableError):
    """Custom error."""

    code = "one-of-required"
    name = "Une des deux colonnes requises"
    tags = ["#head", "#structure"]
    template = "Une des deux colonnes requises : {note}"
    description = ""


class OneOfRequired(CustomCheckMultipleColumns):
    """
    One of required check class
    """
    code = "one-of-required"
    possible_Errors = [OneOfRequiredError]

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__id = self.get("id")
        self.__column1 = self.get("column1")
        self.__column2 = self.get("column2")

    def validate_start(self):
        if self.__column1 not in self.resource.schema.field_names and \
                self.__column2 not in self.resource.schema.field_names:
            note = f"Les deux colonnes {self.__column1!r} et {self.__column2!r} sont manquantes."
            yield OneOfRequiredErrorMissingBothColumns(note=note)

    def validate_row(self, row):
        if self.__column1 not in self.resource.schema.field_names and \
                self.__column2 not in self.resource.schema.field_names:
            # one-of-required error has already been generated in validate_start()
            yield from []
        else:
            cell_value1 = row[self.__column1]
            cell_value2 = row[self.__column2]

            if not valued(cell_value1) and not valued(cell_value2):
                note = f"Au moins l'une des colonnes {self.__column1!r} ou {self.__column2!r} " \
                       "doit comporter une valeur."
                yield OneOfRequiredError.from_row(row, note=note)

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column1", "column2"],
        "properties": {"column1": {"type": "string"}, "column2": {"type": "string"}},
    }
