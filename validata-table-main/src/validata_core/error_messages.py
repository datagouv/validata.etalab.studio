import re
from datetime import datetime
from typing import Dict

import frictionless
import frictionless.errors as ferr

FRENCH_DATE_RE = re.compile(r"^[0-3]\d/[0-1]\d/[12]\d{3}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
CONSTRAINT_RE = re.compile(r'^constraint "([^"]+)" is .*$')
ARRAY_CONSTRAINT_RE = re.compile(r'^array item constraint "([^"]+)" is .*$')


def constraint_name_and_message(
    cell_value, field_def: Dict, constraint_name: str, is_array=False
):
    """Return french name and message for given constraint error."""

    constraint_val = (
        field_def["constraints"][constraint_name]
        if not is_array
        else field_def["arrayItem"]["constraints"][constraint_name]
    )

    if constraint_name == "required":
        return "Cellule vide", "Une valeur doit être renseignée."

    elif constraint_name == "unique":
        return (
            "Valeur déjà présente",
            "Toutes les valeurs de cette colonne doivent être unique.",
        )

    elif constraint_name == "minLength":
        msg = (
            f"Le texte attendu doit comporter au moins {constraint_val} caractère(s)"
            f" (au lieu de {len(cell_value)} actuellement)."
        )
        return "Valeur trop courte", msg

    elif constraint_name == "maxLength":
        msg = (
            f"Le texte attendu ne doit pas comporter plus de {constraint_val}"
            f" caractère(s) (au lieu de {len(cell_value)} actuellement)."
        )
        return "Valeur trop longue", msg

    elif constraint_name == "minimum":
        msg = f"La valeur attendue doit être au moins égale à {constraint_val}."
        return "Valeur trop petite", msg

    elif constraint_name == "maximum":
        msg = f"La valeur attendue doit être au plus égale à {constraint_val}."
        return "Valeur trop grande", msg

    elif constraint_name == "pattern":
        info_list = []
        if "description" in field_def:
            info_list.append(field_def["description"] + "\n")
        if "example" in field_def:
            info_list.append(f"## Exemple(s) valide(s)\n{field_def['example']}\n")
        msg = (
            "\n".join(info_list)
            if info_list
            else "*Aucune description ni exemple à afficher.*"
        )
        return "Format incorrect", msg

    elif constraint_name == "enum":
        enum_values = constraint_val
        if len(enum_values) == 1:
            return (
                "Valeur incorrecte",
                f"L'unique valeur autorisée est : {enum_values[0]}.",
            )
        else:
            md_str = "\n".join([f"- {val}" for val in enum_values])
            return (
                "Valeur incorrecte",
                f"Les seules valeurs autorisées sont :\n{md_str}",
            )


def et_join(values):
    """french enum
    >>> et_join([])
    ''
    >>> et_join(['a'])
    'a'
    >>> et_join(['a','b'])
    'a et b'
    >>> et_join(['a','b','c'])
    'a, b et c'
    >>> et_join(['a','b','c','d','e'])
    'a, b, c, d et e'
    """
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return " et ".join([", ".join(values[:-1]), values[-1]])


def error_translate(err: ferr.Error, schema: frictionless.Schema = None):
    """Translate and improve error message clarity.

    Update err fields:
    - name: use a french name describing the error type
    - message: french error message
    """

    # encoding error
    if isinstance(err, ferr.EncodingError):
        err["name"] = "Erreur d'encodage"
        err[
            "message"
        ] = f"Un problème d'encodage empêche la lecture du fichier ({err.note})"
        return err

    # blank header
    if isinstance(err, ferr.BlankHeaderError):
        err["name"] = "En-tête manquant"
        if len(err.row_positions) == 1:
            err["message"] = f"La colonne n°{err.row_positions[0]} n'a pas d'entête."
        else:
            pos_list = ", ".join(err.row_positions)
            err["message"] = f"Les colonnes n°{pos_list} n'ont pas d'entête."
        return err

    # blank row
    if isinstance(err, ferr.BlankRowError):
        err["name"] = "Ligne vide"
        err["message"] = "Les lignes vides doivent être retirées de la table."
        return err

    # extra cell
    if isinstance(err, ferr.ExtraCellError):
        err["name"] = "Valeur surnuméraire"
        err["message"] = (
            "Le nombre de cellules de cette ligne excède"
            + "le nombre de colonnes défini dans le schéma."
        )
        return err

    # type error
    if isinstance(err, ferr.TypeError):
        field_name = err["fieldName"]
        field_def = next(
            (field for field in schema["fields"] if field["name"] == field_name), None
        )
        field_type = None if field_def is None else field_def.get("type", "string")
        field_format = (
            "default" if field_def is None else field_def.get("format", "default")
        )
        field_value = err["cell"]

        # Date
        if field_type == "date":

            err["name"] = "Format de date incorrect"

            # Checks if date is dd/mm/yyyy
            dm = FRENCH_DATE_RE.match(field_value)
            if dm:
                iso_date = datetime.strptime(field_value, "%d/%m/%Y").strftime(
                    "%Y-%m-%d"
                )
                err["message"] = f"La forme attendue est {iso_date!r}."
                return err

            # Checks if date is yyyy-mm-ddThh:MM:ss
            # print('DATE TIME ? [{}]'.format(field_value))
            dm = DATETIME_RE.match(field_value)
            if dm:
                iso_date = field_value[: field_value.find("T")]
                err["message"] = f"La forme attendue est {iso_date!r}."
                return err

            # default
            err["message"] = "La date doit être écrite sous la forme `aaaa-mm-jj`."

        # Year
        elif field_type == "year":
            err["name"] = "Format d'année incorrect"
            err["message"] = "L'année doit être composée de 4 chiffres."

        # Number
        elif field_type == "number":
            err["name"] = "Format de nombre incorrect"
            if "," in field_value:
                en_number = field_value.replace(",", ".")
                value_str = f"«&#160;{en_number}&#160;»"
                err[
                    "message"
                ] = f"Le séparateur décimal à utiliser est le point ({value_str})."
            else:
                err["message"] = (
                    "La valeur ne doit comporter que des chiffres"
                    " et le point comme séparateur décimal."
                )

        # Number
        elif field_type == "integer":
            err["name"] = "Format entier incorrect"
            err["message"] = "La valeur doit être un nombre entier."

        # String
        elif field_type == "string":
            err["name"] = "Format de chaîne incorrect"
            if field_format == "uri":
                err[
                    "message"
                ] = "La valeur doit être une adresse de site ou de page internet (URL)."
            elif field_format == "email":
                err["message"] = "La valeur doit être une adresse email."
            elif field_format == "binary":
                err["message"] = "La valeur doit être une chaîne encodée en base64."
            elif field_format == "uuid":
                err["message"] = "La valeur doit être un UUID."
            else:
                err["message"] = "La valeur doit être une chaîne de caractères."

        # Boolean
        elif field_type == "boolean":
            true_values = (
                field_def["trueValues"]
                if field_def and "trueValues" in field_def
                else ["true"]
            )
            false_values = (
                field_def["falseValues"]
                if field_def and "falseValues" in field_def
                else ["false"]
            )
            true_values_str = et_join(
                list(map(lambda v: "`{}`".format(v), true_values))
            )
            false_values_str = et_join(
                list(map(lambda v: "`{}`".format(v), false_values))
            )
            err["name"] = "Valeur booléenne incorrecte"
            err["message"] = (
                f"Les valeurs acceptées sont {true_values_str} (vrai)"
                f" et {false_values_str} (faux)."
            )

        return err

    # constraint
    elif isinstance(err, ferr.ConstraintError):
        field_name = err["fieldName"]
        field_def = next(
            (field for field in schema["fields"] if field["name"] == field_name), None
        )

        # extract violated constraint from english message
        m = CONSTRAINT_RE.match(err["note"])
        if m and field_def:
            err["name"], err["message"] = constraint_name_and_message(
                err["cell"], field_def, m[1]
            )
        else:
            # extract violated array constraint from english message
            m = ARRAY_CONSTRAINT_RE.match(err["note"])
            if m and field_def:
                err["name"], err["message"] = constraint_name_and_message(
                    err["cell"], field_def, m[1], is_array=True
                )
            else:
                err["name"] = "Contrainte non respectée"
                err["message"] = err["note"]

    # missing header
    elif isinstance(err, ferr.MissingLabelError):
        field_name = err["fieldName"]
        err["name"] = "Colonne obligatoire manquante"
        err["message"] = f"La colonne obligatoire `{field_name}` est manquante."

    return err
