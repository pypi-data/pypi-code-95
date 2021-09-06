from hestia_earth.schema import IndicatorStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product, get_site
from hestia_earth.models.utils.cycle import calculate_land_occupation
from hestia_earth.models.utils.input import sum_input_impacts
from .utils import get_region_factor
from . import MODEL

TERM_ID = 'biodiversityLossLandOccupation'


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(impact_assessment: dict, product: dict, occupation_factor: float):
    cycle = impact_assessment.get('cycle', {})
    site = get_site(impact_assessment)
    landOccupation = calculate_land_occupation(cycle, site, product) or 0
    inputs_value = sum_input_impacts(cycle.get('inputs', []), TERM_ID)
    logger.debug('model=%s, term=%s, inputs value=%s', MODEL, TERM_ID, inputs_value)
    value = landOccupation * occupation_factor + inputs_value
    return _indicator(value) if value else None


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment) or {}
    product_id = product.get('term', {}).get('@id')
    factor = get_region_factor(impact_assessment, 'occupation')

    debugRequirements(model=MODEL, term=TERM_ID,
                      product_id=product_id,
                      occupation_factor=factor)

    should_run = all([product_id, factor])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, product, factor


def run(impact_assessment: dict):
    should_run, product, occupation_factor = _should_run(impact_assessment)
    return _run(impact_assessment, product, occupation_factor) if should_run else None
