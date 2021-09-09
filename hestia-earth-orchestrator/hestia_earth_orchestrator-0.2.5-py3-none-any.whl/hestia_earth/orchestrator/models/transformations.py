from copy import deepcopy
from functools import reduce
from hestia_earth.schema import CompletenessJSONLD
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from . import run as run_node
from hestia_earth.orchestrator.utils import _new_practice, _filter_by_keys, find_term_match


def _full_completeness():
    completeness = CompletenessJSONLD().to_dict()
    keys = list(completeness.keys())
    keys.remove('@type')
    return {
        '@type': completeness['@type'],
        **reduce(lambda prev, curr: {**prev, curr: True}, keys, {})
    }


def _include_practice(practice: dict):
    term = practice.get('term', {})
    term_type = term.get('termType')
    term_id = term.get('@id')
    lookup = download_lookup(f"{term_type}.csv")
    value = get_table_value(lookup, 'termid', term_id, column_name('includeForTransformation'))
    return False if value is None or value == '' or not value else True


def _apply_transformation_share(previous: dict, current: dict):
    share = current.get('previousTransformationShare', 100)
    products = previous.get('products', [])

    def replace_value(input: dict):
        product_values = find_term_match(products, input.get('term', {}).get('@id')).get('value', [])
        should_replace = len(product_values) > 0 and len(input.get('value', [])) == 0
        return {
            **input,
            **({'value': [v * share / 100 for v in product_values]} if should_replace else {})
        }

    current['inputs'] = list(map(replace_value, current.get('inputs', [])))
    return current


def _convert_transformation(cycle: dict, transformation: dict):
    data = deepcopy(transformation)
    # copy data from previous transformation
    data['dataCompleteness'] = _full_completeness()
    data['functionalUnit'] = cycle.get('functionalUnit')
    data['site'] = cycle.get('site')
    data['cycleDuration'] = transformation.get('transformationDuration', cycle.get('cycleDuration'))
    data['startDate'] = transformation.get('startDate', cycle.get('startDate'))
    data['endDate'] = transformation.get('endDate', cycle.get('endDate'))
    data['practices'] = [
        _new_practice(transformation.get('term'))  # add `term` as a Practice
    ] + transformation.get('practices', []) + [
        p for p in cycle.get('practices', []) if _include_practice(p)  # some practices need to be copied over
    ]
    return data


def _run_transformation(cycle: dict, transformation: dict, models: list):
    data = _convert_transformation(cycle, transformation)
    result = run_node(data, models)
    return _filter_by_keys(result, ['term', 'inputs', 'products', 'emissions'])


def _first_transformation(transformations: list):
    return next((t for t in transformations if t.get('previousTransformationTerm') is None), None)


def _next_transformation(previous: dict, transf: list):
    previous_term = previous.get('term', {}).get('@id')
    return (
        next((v for v in transf if v.get('previousTransformationTerm', {}).get('@id') == previous_term), None)
    ) if previous_term else _first_transformation(transf)


def _run_serie(cycle: dict, previous: dict, transformations: list, models: list):
    transformation = _next_transformation(previous, transformations)
    transformation = _apply_transformation_share(previous, transformation) if transformation else None
    result = _run_transformation(cycle, transformation, models) if transformation else None
    # if no next transformation, stop the loop
    return ([result] + _run_serie(cycle, result, transformations, models)) if transformation else []


def run(models: list, cycle: dict):
    transformations = cycle.get('transformations', [])
    results = _run_serie(cycle, cycle, transformations, models)
    return results
