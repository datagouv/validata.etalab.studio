import phonenumbers
from frictionless import errors

from .utils import CustomCheckSingleColumn


def is_valid_number_for_country(phone_number: str, *, country_code=None):
    """Check if a phone number, giving an optional country_code.

    If country code is given, an additional check for valid_short_number is done.
    """
    try:
        pn = phonenumbers.parse(phone_number, country_code)
    except phonenumbers.NumberParseException:
        return False

    std_valid = phonenumbers.is_valid_number(pn)
    return (
        std_valid
        if country_code is None
        else std_valid or phonenumbers.is_valid_short_number(pn)
    )


def is_valid_phone_number(phonenumber: str):
    """Check if a phone number is a french or international valid one."""
    return is_valid_number_for_country(
        phonenumber, country_code="FR"
    ) or is_valid_number_for_country(phonenumber)


class PhoneNumberValueError(errors.CellError):
    """Custom error."""

    code = "phone-number-value"
    name = "Numéro de téléphone invalide"
    tags = ["#body"]
    template = (
        "La valeur '{cell}' n'est pas un numéro de téléphone valide.\n\n"
        " Les numéros de téléphone acceptés sont les numéros français à 10 chiffres"
        " (`01 99 00 27 37`) ou au format international avec le préfixe du pays"
        " (`+33 1 99 00 27 37`). Les numéros courts (`115` ou `3949`) sont"
        " également acceptés."
    )
    description = ""


class PhoneNumberValue(CustomCheckSingleColumn):
    """Check phone number validity."""

    code = "phone-number-value"
    possible_Errors = [PhoneNumberValueError]  # type: ignore

    def _validate_start(self):
        yield from []

    def _validate_row(self, cell_value, row):
        if not is_valid_phone_number(cell_value):
            yield PhoneNumberValueError.from_row(row, note="", field_name=self.get('column'))

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }
