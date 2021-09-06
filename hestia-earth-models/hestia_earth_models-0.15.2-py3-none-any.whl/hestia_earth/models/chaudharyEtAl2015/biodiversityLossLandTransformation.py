from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import emission_value
from hestia_earth.models.utils.input import sum_input_impacts
from .utils import get_region_factor
from . import MODEL

TERM_ID = 'biodiversityLossLandTransformation'
TRANSFORMATION_TERM_IDS = [
    'landTransformationFromForest20YearAverage',
    'landTransformationFromOtherNaturalVegetation20YearAverage'
]


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(impact_assessment: dict, transformation_value: float, transformation_factor: float):
    cycle = impact_assessment.get('cycle', {})
    inputs_value = sum_input_impacts(cycle.get('inputs', []), TERM_ID)
    logger.debug('model=%s, term=%s, inputs value=%s', MODEL, TERM_ID, inputs_value)
    value = transformation_value * transformation_factor + inputs_value
    return _indicator(value) if value else None


def _total_transformation(impact_assessment: dict):
    values = [emission_value(impact_assessment, term_id) for term_id in TRANSFORMATION_TERM_IDS]
    return list_sum(list(filter(lambda v: v is not None, values)), None)


def _should_run(impact_assessment: dict):
    value = _total_transformation(impact_assessment)
    factor = get_region_factor(impact_assessment, 'transformation')

    debugRequirements(model=MODEL, term=TERM_ID,
                      transformation_value=value,
                      transformation_factor=factor)

    should_run = all([value, factor])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, value, factor


def run(impact_assessment: dict):
    should_run, transformation_value, transformation_factor = _should_run(impact_assessment)
    return _run(impact_assessment, transformation_value, transformation_factor) if should_run else None
