from hestia_earth.schema import InputStatsDefinition
from hestia_earth.utils.lookup import get_table_value, download_lookup
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'seed'


def _input(value: float, sd: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    input['statsDefinition'] = InputStatsDefinition.REGIONS.value
    if sd > 0:
        input['sd'] = [sd]
    return input


def _run_product(lookup):
    def run(product: dict):
        term_id = product.get('term', {}).get('@id', '')
        product_value = list_sum(product.get('value', []))
        value = safe_parse_float(get_table_value(lookup, 'termid', term_id, 'seed_output_kg_avg')) * product_value
        logger.info('model=%s, term=%s, value=%s', MODEL, term_id, value)
        sd = safe_parse_float(get_table_value(lookup, 'termid', term_id, 'seed_output_kg_sd'))
        return value, sd
    return run


def _run(products: list):
    lookup = download_lookup('crop.csv', True)
    values = list(map(_run_product(lookup), products))
    total_value = list_sum([value for value, _ in values])
    # TODO: we only fill-in sd for single values as the total value is complicated to calculate
    total_sd = values[0][1] if len(values) == 1 else 0
    return [_input(total_value, total_sd)] if total_value > 0 else []


def _should_run_product(lookup):
    def run(product: dict):
        term_id = product.get('term', {}).get('@id', '')
        product_value = list_sum(product.get('value', []))
        in_lookup = term_id in list(lookup.termid)
        should_run = in_lookup and product_value > 0
        logger.debug('model=%s, term=%s, should_run=%s', MODEL, term_id, should_run)
        return should_run
    return run


def _should_run(cycle: dict):
    lookup = download_lookup('crop.csv', True)
    products = list(filter(_should_run_product(lookup), cycle.get('products', [])))
    should_run = valid_site_type(cycle) and _is_term_type_incomplete(cycle, TERM_ID) and len(products) > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
