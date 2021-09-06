from functools import reduce
from hestia_earth.utils.tools import flatten, non_empty_list, list_average

from hestia_earth.aggregation.log import logger
from hestia_earth.aggregation.utils import _min, _max, _sd


def _aggregate(nodes: list):
    first_node = nodes[0]
    term = first_node.get('term')
    values = non_empty_list(flatten([node.get('value') for node in nodes]))
    value = list_average(values)
    logger.debug('term: %s, values: %s', term.get('@id'), ', '.join([str(v) for v in values]))
    observations = len(nodes)
    return {
        'node': first_node,
        'term': term,
        'value': value if len(values) > 0 else None,
        'max': _max(values),
        'min': _min(values),
        'sd': _sd(values),
        'observations': observations
    }


def _aggregate_term(aggregates_map: dict):
    def aggregate(term_id: str):
        nodes = aggregates_map.get(term_id, [])
        return _aggregate(nodes) if len(nodes) > 0 else None
    return aggregate


def _aggregate_nodes(aggregate_key: str):
    def aggregate(data: dict):
        terms = data.get(aggregate_key).keys()
        aggregates = non_empty_list(map(_aggregate_term(data.get(aggregate_key)), terms))
        return (aggregates, data) if len(aggregates) > 0 else ([], {})

    def aggregate_multiple(data: dict):
        return reduce(
            lambda prev, curr: {**prev, curr: _aggregate_nodes(curr)(data)}, aggregate_key, {}
        )

    return aggregate if isinstance(aggregate_key, str) else aggregate_multiple


def aggregate(aggregate_key: str, groups: dict) -> list:
    return non_empty_list(map(_aggregate_nodes(aggregate_key), groups.values()))
