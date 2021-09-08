from hestia_earth.schema import IndicatorStatsDefinition, TermTermType
from hestia_earth.utils.tools import list_sum
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product, convert_value_from_cycle
from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from . import MODEL

TERM_ID = 'freshwaterWithdrawals'


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(product: dict, irrigation: float):
    value = convert_value_from_cycle(product, irrigation) if irrigation > 0 else 0
    return [] if value is None else [_indicator(value)]


def _get_irrigation(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    data_complete = _is_term_type_complete(cycle, {'termType': TermTermType.WATER.value})
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.WATER)
    value = list_sum(get_total_value(inputs))
    return None if len(inputs) == 0 and not data_complete else value


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment) or {}
    product_id = product.get('term', {}).get('@id')
    irrigation = _get_irrigation(impact_assessment)

    debugRequirements(model=MODEL, term=TERM_ID,
                      product=product_id,
                      irrigation=irrigation)

    should_run = all([product_id, irrigation is not None])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, product, irrigation


def run(impact_assessment: dict):
    should_run, product, irrigation = _should_run(impact_assessment)
    return _run(product, irrigation) if should_run else []
