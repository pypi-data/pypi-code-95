from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.input import get_inorganic_fertilizer_N_total
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL
from .no3ToGroundwaterAllOrigins import _should_run, _get_value

TERM_ID = 'no3ToGroundwaterInorganicFertilizer'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, content_list_of_items: list):
    no3ToGroundwaterAllOrigins = _get_value(content_list_of_items)
    value = get_inorganic_fertilizer_N_total(cycle)
    return [_emission(value * no3ToGroundwaterAllOrigins)]


def run(cycle: dict):
    should_run, content_list_of_items = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(cycle, content_list_of_items) if should_run else []
