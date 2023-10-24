"""
    Comme indiqué par Loïc Haÿ dans son mail du 5/7/2018

> Document de référence dans les spécifications SCDL :
> http://www.moselle.gouv.fr/content/download/1107/7994/file/nomenclature.pdf
>
> Dans la nomenclature Actes, les valeurs avant le "/" sont :
>
> Commande publique
> Urbanisme
> Domaine et patrimoine
> Fonction publique
> Institutions et vie politique
> Libertés publiques et pouvoirs de police
> Finances locales
> Domaines de compétences par thèmes
> Autres domaines de compétences
>
> Le custom check devra accepter minuscules et majuscules, accents et sans accents ...

    Pierre Dittgen, JailBreak
"""
import unicodedata

from frictionless import errors

from .utils import CustomCheckSingleColumn

# Module API

AUTHORIZED_VALUES = [
    "Commande publique",
    "Urbanisme",
    "Domaine et patrimoine",
    "Fonction publique",
    "Institutions et vie politique",
    "Libertés publiques et pouvoirs de police",
    "Finances locales",
    "Domaines de compétences par thèmes",
    "Autres domaines de compétences",
]


class NomenclatureActesValueError(errors.CellError):
    """Custom error."""

    code = "nomenclature-actes-value"
    name = "Actes de nomenclature"
    tags = ["#body"]
    template = (
        "La valeur {cell!r} ne respecte pas le format des nomenclatures d'actes"
        " ({note})"
    )
    description = ""


class NomenclatureActesValue(CustomCheckSingleColumn):

    code = "nomenclature-actes-value"
    possible_Errors = [NomenclatureActesValueError]  # type: ignore

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__nomenclatures = set(map(norm_str, AUTHORIZED_VALUES))

    def _validate_start(self):
        yield from []

    def _validate_row(self, cell_value, row):
        if "/" not in cell_value:
            note = "le signe oblique « / » est manquant"
            yield NomenclatureActesValueError.from_row(
                row, note=note, field_name=self.get('column')
            )
            return

        nomenc = cell_value[: cell_value.find("/")]

        # Nomenclature reconnue et pas d'espace avant ni après l'oblique
        if norm_str(nomenc) in self.__nomenclatures and "/ " not in cell_value:
            return

        if norm_str(nomenc.rstrip()) in self.__nomenclatures or "/ " in cell_value:
            note = "Le signe oblique ne doit pas être précédé ni suivi d'espace"
        else:
            note = f"le préfixe de nomenclature Actes {nomenc!r} n'est pas reconnu"

        yield NomenclatureActesValueError.from_row(
            row, note=note, field_name=self.get('column')
        )

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }


def norm_str(s):
    """ Normalize string, i.e. removing accents and turning into lowercases """
    return "".join(
        c
        for c in unicodedata.normalize("NFD", s.lower())
        if unicodedata.category(c) != "Mn"
    )
