import pytest
from pathlib import Path
from validata_core import validate
from tests.tests_validata_core import utils


@pytest.fixture
def schema_subventions():
    return "https://gitlab.com/opendatafrance/scdl/subventions/-/raw/master/schema.json"


EXAMPLES_DIRECTORY_PATH = Path("tests/tests_validata_core/examples_subventions_one_of_required/")


def test_one_of_required_check_valid(schema_subventions):
    #  Exemples valides :
    #   - pas de colonne RnaBenficiaire mais idBeneficiaire rempli et valide : exemple_valide_subventions1.csv
    #   - pas de colonne iDBeneficiaire mais rnaBeneficiaire rempli et valide : exemple_valide_subventions2.csv
    #   - les deux colonnes sont remplies et au bon format : exemple_valide_subventions3.csv

    sources_valides = [
        "exemple_valide_subventions1.csv",
        "exemple_valide_subventions2.csv",
        "exemple_valide_subventions3.csv"
    ]

    for source in sources_valides:
        full_path_source = EXAMPLES_DIRECTORY_PATH / source
        report = validate(full_path_source, schema_subventions)
        assert report.valid


def test_one_of_required_check_invalid_with_one_of_required_error(schema_subventions):
    #  Exemples invalides avec one-of-required error:
    #  - Les deux colonnes existent mais aucun des champs idBeneficiaire et rnaBeneficiaire n'a de valeurs remplies :
    #    exemple_invalide_subventions_one_of_required1.csv

    #  - La colonne idBeneficiaire n'existe pas et la valeur de rnaBeneficiaire n'est pas remplie :
    #    exemple_invalide_subventions_one_of_required2.csv

    #  - La colonne rnaBeneficiaire n'existe pas et la valeur de idBeneficiaire n'est pas remplie :
    #    exemple_invalide_subventions_one_of_required3.csv

    #  - Pas de colonnes idBeneficiaire ni rnaBeneficiaire : exemple_invalide_subventions_one_of_required4.csv
    #    (Pour ce cas-ci, le message d'erreur est différent des 3 permiers cas)

    sources = [
        "exemple_invalide_subventions_one_of_required1.csv",
        "exemple_invalide_subventions_one_of_required2.csv",
        "exemple_invalide_subventions_one_of_required3.csv",
    ]

    for source in sources:
        full_path_source = EXAMPLES_DIRECTORY_PATH / source
        report = validate(full_path_source, schema_subventions)

        error = utils.check_invalid_report_with_one_single_error(report)
        assert error["code"] == "one-of-required"
        assert "Au moins l'une des colonnes 'idBeneficiaire' ou 'rnaBeneficiaire' doit comporter une valeur." \
               in error["message"]

    source = EXAMPLES_DIRECTORY_PATH / "exemple_invalide_subventions_one_of_required4.csv"
    report = validate(source, schema_subventions)

    error = utils.check_invalid_report_with_one_single_error(report)
    assert error["code"] == "one-of-required"
    assert "Une des deux colonnes requises : Les deux colonnes 'idBeneficiaire' et 'rnaBeneficiaire' sont manquantes." \
           in error["message"]


def test_one_of_required_check_invalid_with_constraint_error(schema_subventions):
    # Exemples invalides avec constraint-error (erreur de format sur le numéro RNA du champs rnaBeneficiaire) :
    #    - Les deux colonnes existent, et seul le numéro rnaBeneficiaire est complété
    #      mais sa valeur n'est pas correcte en termes de format attendu :
    #      exemple_invalide_subventions_constraint_error1.csv

    #    - La colonne idBeneficiaire n'existe pas et le numéro rnaBeneficiaire est complété mais sa valeur n'est pas
    #      correcte en termes de format attendu : exemple_invalide_subventions_constraint_error2.csv

    sources = [
        "exemple_invalide_subventions_constraint_error1.csv",
        "exemple_invalide_subventions_constraint_error2.csv"
    ]

    for source in sources:
        full_path_source = EXAMPLES_DIRECTORY_PATH / source
        report = validate(full_path_source, schema_subventions)

        error = utils.check_invalid_report_with_one_single_error(report)
        assert error["code"] == "constraint-error"
        assert " débutant par 'W' et composé de 9 chiffres" in error["message"]


def test_one_of_required_check_invalid_with_french_siret_error(schema_subventions):
    #  Exemple invalide avec french-siret-value error (erreur de format sur le numéro SIRET du champs idBeneficiaire):
    #   - La colonne rnaBeneficiaire n'existe pas et le numéro Siret de l'idBeneficiaire est complété mais sa valeur
    #     ne respecte pas le french-siret-value custom check : exemple_invalide_subventions_french_siret_error1.csv

    #   - Les deux colonnes existent, et seul le numéro Siret idBeneficiaire est complété mais sa valeur ne
    #     respecte pas le french-siret-value custom check : exemple_invalide_subventions_french_siret_error2.csv

    sources = [
        "exemple_invalide_subventions_french_siret_error1.csv",
        "exemple_invalide_subventions_french_siret_error2.csv"
    ]

    for source in sources:
        full_path_source = EXAMPLES_DIRECTORY_PATH / source
        report = validate(full_path_source, schema_subventions)

        error = utils.check_invalid_report_with_one_single_error(report)
        assert error["code"] == "french-siret-value"
        assert " n'est pas un numéro SIRET français valide." in error["message"]
