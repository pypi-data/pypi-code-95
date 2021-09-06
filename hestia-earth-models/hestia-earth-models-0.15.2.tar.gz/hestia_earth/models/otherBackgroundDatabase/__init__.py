from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from hestia_earth.models.log import logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.term import get_emission_inputs_production_terms
from hestia_earth.models.utils.input import load_impacts

MODEL = 'otherBackgroundDatabase'
MODEL_KEY = 'impactAssessment'


def _emission_group(term_id: str):
    lookup = download_lookup('emission.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('inputProductionGroupId'))


def _group_emissions(impact: dict):
    def _group_by(prev: dict, emission: dict):
        term_id = emission.get('term', {}).get('@id')
        grouping = _emission_group(term_id)
        prev[grouping] = prev.get(grouping, 0) + emission.get('value', 0)
        return prev

    emissions = impact.get('emissionsResourceUse', [])
    return reduce(_group_by, emissions, {})


def _get_input_value(input: dict, emission: str):
    impact = input.get(MODEL_KEY)
    # group all emissions so that we only take the final "Inputs Production" value
    emissions = _group_emissions(impact)
    return sum(input.get('value', [])) * emissions.get(emission, 0)


def _get_value(emission: str, inputs: list):
    return reduce(lambda prev, i: prev + _get_input_value(i, emission), inputs, 0)


def _emission(term_id: str, inputs: list):
    value = _get_value(term_id, inputs)
    logger.info('model=%s, term=%s, value=%s', MODEL, term_id, value)
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.BACKGROUND.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['inputs'] = list(map(lambda i: i.get('term'), inputs))
    return emission


def run(term: str, cycle: dict):
    run_all_terms = term is None or term == '' or term == 'null' or term == 'all'
    terms = get_emission_inputs_production_terms()
    inputs = load_impacts(cycle.get('inputs', []))
    logger.debug('model=%s, nb inputs=%s', MODEL, len(inputs))
    emissions = [] if len(inputs) == 0 else (
        [_emission(term, inputs) for term in terms] if run_all_terms else [_emission(term, inputs)]
    )
    return list(filter(lambda e: len(e.get('inputs', [])) > 0, emissions))
