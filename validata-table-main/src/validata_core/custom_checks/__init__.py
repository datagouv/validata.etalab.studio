from .cohesive_columns_value import CohesiveColumnsValue
from .compare_columns_value import CompareColumnsValue
from .french_gps_coordinates import FrenchGPSCoordinates
from .french_siren_value import FrenchSirenValue
from .french_siret_value import FrenchSiretValue
from .missing_required_header import MissingRequiredHeader  # noqa
from .nomenclature_actes_value import NomenclatureActesValue
from .opening_hours_value import OpeningHoursValue
from .phone_number_value import PhoneNumberValue
from .sum_columns_value import SumColumnsValue
from .year_interval_value import YearIntervalValue
from .one_of_required import OneOfRequired

# Please keep the below dict up-to-date
available_checks = {
    CohesiveColumnsValue.code: CohesiveColumnsValue,
    CompareColumnsValue.code: CompareColumnsValue,
    FrenchGPSCoordinates.code: FrenchGPSCoordinates,
    FrenchSirenValue.code: FrenchSirenValue,
    FrenchSiretValue.code: FrenchSiretValue,
    NomenclatureActesValue.code: NomenclatureActesValue,
    OpeningHoursValue.code: OpeningHoursValue,
    PhoneNumberValue.code: PhoneNumberValue,
    SumColumnsValue.code: SumColumnsValue,
    YearIntervalValue.code: YearIntervalValue,
    OneOfRequired.code: OneOfRequired,
}
