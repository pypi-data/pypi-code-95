import math
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import search
from hestia_earth.utils.model import find_primary_product, find_term_match, linked_node
from hestia_earth.utils.tools import safe_parse_date

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.cycle import is_organic, valid_site_type

MODEL = 'aggregated'
MODEL_KEY = 'impactAssessment'
SEED_TERM_ID = 'seed'
MATCH_WORLD_QUERY = {'match': {'country.name.keyword': {'query': 'World', 'boost': 1}}}


def _end_date(end_date: str):
    year = safe_parse_date(end_date).year
    return round((math.floor(year / 10) + 1) * 10)


def _match_country(country: dict):
    country_name = country.get('name') if country else None
    return {
        'bool': {
            # either get with exact country, or default to global
            'should': [
                {'match': {'country.name.keyword': {'query': country_name, 'boost': 1000}}},
                MATCH_WORLD_QUERY
            ],
            'minimum_should_match': 1
        }
    } if country_name else MATCH_WORLD_QUERY


def _find_closest_impact(cycle: dict, end_date: str, input: dict, country: dict = None):
    query = {
        'bool': {
            'must': [
                {'match': {'@type': SchemaType.IMPACTASSESSMENT.value}},
                {'match': {'aggregated': 'true'}},
                {'match': {'product.name.keyword': input.get('term', {}).get('name')}},
                _match_country(country)
            ],
            'should': [
                # if the Cycle is organic, we can try to match organic aggregate first
                {'match': {'name': {'query': 'Organic' if is_organic(cycle) else 'Conventional', 'boost': 1000}}},
                {'match': {'endDate': _end_date(end_date)}}
            ]
        }
    }
    results = search(query)
    result = results[0] if len(results) > 0 else {}
    logger.debug('model=%s, term=%s, impact=%s', MODEL, input.get('term', {}).get('@id'), result.get('@id'))
    return result


def _run_seed(cycle: dict, product: dict, input: dict, end_date: str):
    impact = _find_closest_impact(cycle, end_date, product, input.get('country'))
    return [{**input, MODEL_KEY: linked_node(impact)}] if impact else []


def _should_run_seed(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    term_type = primary_product.get('term', {}).get('termType')
    input = find_term_match(cycle.get('inputs', []), SEED_TERM_ID, None)

    debugRequirements(model=MODEL, term=SEED_TERM_ID,
                      primary_product=primary_product.get('@id'),
                      term_type=term_type,
                      has_input=input is not None)

    should_run = term_type == TermTermType.CROP.value and input is not None and valid_site_type(cycle, True)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, SEED_TERM_ID, should_run)
    return should_run, primary_product, input


def _run(cycle: dict, inputs: list, end_date: str):
    inputs = [
        {**i, MODEL_KEY: linked_node(_find_closest_impact(cycle, end_date, i, i.get('country')))} for i in inputs
    ]
    return list(filter(lambda i: i.get(MODEL_KEY).get('@id') is not None, inputs))


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    # do not override inputs that already have an impactAssessment
    inputs = [i for i in cycle.get('inputs', []) if not i.get(MODEL_KEY)]

    debugRequirements(model=MODEL, term=MODEL_KEY,
                      end_date=end_date,
                      nb_inputs=len(inputs))

    should_run = all([end_date, len(inputs) > 0])
    logger.info('model=%s, should_run=%s', MODEL, should_run)
    return should_run, inputs, end_date


def run(cycle: dict):
    should_run, inputs, end_date = _should_run(cycle)
    should_run_seed, primary_product, seed_input = _should_run_seed(cycle)
    return _run(cycle, inputs, end_date) + (
        _run_seed(cycle, primary_product, seed_input, end_date) if should_run_seed else []
    ) if should_run else []
