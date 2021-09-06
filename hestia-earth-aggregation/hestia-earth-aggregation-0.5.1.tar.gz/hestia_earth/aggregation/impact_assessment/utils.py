from hestia_earth.schema import SchemaType
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.model import linked_node

from hestia_earth.aggregation.utils import _aggregated_version, _aggregated_node, _set_dict_single
from hestia_earth.aggregation.utils.term import _update_country, _format_country_name
from .indicator import _new_indicator

AGGREGATION_KEY = 'emissionsResourceUse'


def _format_aggregate(aggregate: dict):
    term = aggregate.get('term')
    value = aggregate.get('value')
    min = aggregate.get('min')
    max = aggregate.get('max')
    sd = aggregate.get('sd')
    observations = aggregate.get('observations')
    node = _new_indicator(term, value)
    _set_dict_single(node, 'observations', observations)
    _set_dict_single(node, 'min', min)
    _set_dict_single(node, 'max', max)
    _set_dict_single(node, 'sd', sd, True)
    return _aggregated_version(node, 'min', 'max', 'sd', 'observations')


def _format_terms_results(results: tuple):
    aggregates, data = results
    impacts = data.get('nodes', [])
    return {
        **_create_impact_assessment(impacts[0]),
        AGGREGATION_KEY: list(map(_format_aggregate, aggregates))
    } if len(impacts) > 0 else None


def _format_world_results(results: tuple):
    return {
        **_format_terms_results(results),
        'organic': False,
        'irrigated': False
    }


def _format_country_results(results: tuple):
    _, data = results
    impact = data.get('nodes', [])[0]
    return {
        **_format_world_results(results),
        'name': _impact_assessment_name(impact, False),
        'id': _impact_assessment_id(impact, False)
    }


def _impact_assessment_id(n: dict, include_matrix=True):
    # TODO: handle impacts that dont have organic/irrigated version => only 1 final version
    return '-'.join(non_empty_list([
        n.get('product', {}).get('@id'),
        _format_country_name(n.get('country', {}).get('name')),
        ('organic' if n.get('organic', False) else 'conventional') if include_matrix else '',
        ('irrigated' if n.get('irrigated', False) else 'non-irrigated') if include_matrix else '',
        n.get('startDate'),
        n.get('endDate')
    ]))


def _impact_assessment_name(n: dict, include_matrix=True):
    return ' - '.join(non_empty_list([
        n.get('product', {}).get('name'),
        n.get('country', {}).get('name'),
        ', '.join(non_empty_list([
            ('Organic' if n.get('organic', False) else 'Conventional') if include_matrix else '',
            ('Irrigated' if n.get('irrigated', False) else 'Non Irrigated') if include_matrix else ''
        ])),
        '-'.join([n.get('startDate'), n.get('endDate')])
    ]))


def _create_impact_assessment(data: dict):
    impact = {'type': SchemaType.IMPACTASSESSMENT.value}
    # copy properties from existing ImpactAssessment
    impact['startDate'] = data.get('startDate')
    impact['endDate'] = data.get('endDate')
    impact['product'] = linked_node(data.get('product'))
    impact['functionalUnitQuantity'] = data.get('functionalUnitQuantity')
    impact['allocationMethod'] = data.get('allocationMethod')
    impact['systemBoundary'] = data.get('systemBoundary')
    impact['organic'] = data.get('organic', False)
    impact['irrigated'] = data.get('irrigated', False)
    impact['dataPrivate'] = False
    if data.get('country'):
        impact['country'] = data['country']
    return _aggregated_node(impact)


def _update_impact_assessment(country_name: str, start: int, end: int, source: dict = None, include_matrix=True):
    def update(impact: dict):
        impact['startDate'] = str(start)
        impact['endDate'] = str(end)
        impact['country'] = _update_country(country_name) if country_name else impact.get('country')
        impact['name'] = _impact_assessment_name(impact, include_matrix)
        impact['id'] = _impact_assessment_id(impact, include_matrix)
        return impact if source is None else {**impact, 'source': source}
    return update


def _remove_duplicated_impact_assessments(impacts: list):
    def filter_impact(impact: dict):
        # removes non-organic + non-irrigated original impacts (they are recalculated by country average)
        return impact.get('organic', False) or impact.get('irrigated', False) \
            or 'conventional-non-irrigated' not in impact.get('id')

    return list(filter(filter_impact, impacts))
