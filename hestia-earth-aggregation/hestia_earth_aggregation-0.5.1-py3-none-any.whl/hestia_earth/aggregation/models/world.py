from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float, flatten

from hestia_earth.aggregation.log import logger
from hestia_earth.aggregation.utils import _min, _max, _sd
from hestia_earth.aggregation.utils.term import DEFAULT_REGION_ID

LOOKUP_GROUPING = {
    TermTermType.CROP.value: download_lookup(f"{TermTermType.CROP.value}.csv", True),
    TermTermType.ANIMALPRODUCT.value: download_lookup(f"{TermTermType.ANIMALPRODUCT.value}.csv", True)
}
LOOKUP_GROUPING_COLUMN = {
    TermTermType.CROP.value: 'cropGroupingFAOSTAT',
    TermTermType.ANIMALPRODUCT.value: 'animalProductGroupingFAO'
}


def _lookup(product: dict):
    term_type = product.get('termType')
    try:
        lookup = LOOKUP_GROUPING[term_type]
        grouping_column = LOOKUP_GROUPING_COLUMN[term_type]
        grouping = get_table_value(lookup, 'termid', product.get('@id'), column_name(grouping_column))
        return download_lookup(f"region-{term_type}-{grouping_column}-productionQuantity.csv", True), grouping
    except Exception:
        return None, None


def _get_weight(lookup, lookup_column: str, country_id: str, year: int):
    country_value = get_table_value(lookup, 'termid', country_id, column_name(lookup_column))
    country_value = extract_grouped_data_closest_date(country_value, year)
    world_value = get_table_value(lookup, 'termid', DEFAULT_REGION_ID, column_name(lookup_column))
    world_value = extract_grouped_data_closest_date(world_value, year)
    percent = safe_parse_float(country_value, 1) / safe_parse_float(world_value, 1)
    logger.debug('weight, country=%s, year=%s, percent=%s', country_id, year, percent)
    return percent


def _weighted_value(lookup, lookup_column: str):
    def apply(node: dict):
        country_id = node.get('country').get('@id')
        weight = _get_weight(lookup, lookup_column, country_id, node.get('year')) if lookup is not None else 1
        value = node.get('value')
        return (list_sum(value, value), weight) if value is not None else None
    return apply


def _aggregate_weighted(term: dict, nodes: list, product: dict):
    lookup, lookup_column = _lookup(product)
    values = non_empty_list(map(_weighted_value(lookup, lookup_column), nodes))
    weighted_value = [value * weight for value, weight in values]
    value = sum(weighted_value)
    percent = sum(weight for _v, weight in values)
    value = value / percent if percent != 0 else value
    logger.debug('product=%s, term: %s, value: %s', product.get('@id'), term.get('@id'), str(value))
    observations = sum(flatten([node.get('observations', 1) for node in nodes]))
    return {
        'node': nodes[0],
        'term': term,
        'value': value if len(values) > 0 else None,
        'max': _max(weighted_value),
        'min': _min(weighted_value),
        'sd': _sd(weighted_value),
        'observations': observations
    }


def _aggregate_nodes(aggregate_key: str):
    def aggregate(data: dict):
        product = data.get('product')

        def aggregate(term_id: str):
            nodes = data.get(aggregate_key).get(term_id)
            term = nodes[0].get('term')
            return _aggregate_weighted(term, nodes, product)

        aggregates = flatten(map(aggregate, data.get(aggregate_key, {}).keys()))
        return (aggregates, data) if len(aggregates) > 0 else ([], {})

    def aggregate_multiple(data: dict):
        return reduce(
            lambda prev, curr: {**prev, curr: _aggregate_nodes(curr)(data)}, aggregate_key, {}
        )

    return aggregate if isinstance(aggregate_key, str) else aggregate_multiple


def aggregate(aggregate_key: str, groups: dict) -> list:
    return non_empty_list(map(_aggregate_nodes(aggregate_key), groups.values()))
