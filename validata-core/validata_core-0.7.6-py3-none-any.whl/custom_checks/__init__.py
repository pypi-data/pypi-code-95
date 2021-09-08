from .cohesive_columns_value import CohesiveColumnsValue
from .compare_columns_value import CompareColumnsValue
from .french_siren_value import FrenchSirenValue
from .french_siret_value import FrenchSiretValue
from .missing_required_header import MissingRequiredHeader  # noqa
from .nomenclature_actes_value import NomenclatureActesValue
from .sum_columns_value import SumColumnsValue
from .year_interval_value import YearIntervalValue

# Please keep the below dict up-to-date
available_checks = {
    "cohesive-columns-value": CohesiveColumnsValue,
    "compare-columns-value": CompareColumnsValue,
    "french-siren-value": FrenchSirenValue,
    "french-siret-value": FrenchSiretValue,
    "nomenclature-actes-value": NomenclatureActesValue,
    "sum-columns-value": SumColumnsValue,
    "year-interval-value": YearIntervalValue,
}
