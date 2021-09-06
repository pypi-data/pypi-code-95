from functools import reduce
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float, flatten

from hestia_earth.aggregation.log import logger
from hestia_earth.aggregation.utils import _end_date_year, _min, _max, _sd


def _organic_weight(country_id: str, year: int):
    lookup = download_lookup('region-standardsLabels-isOrganic.csv', True)
    data = get_table_value(lookup, 'termid', country_id, 'organic')
    percent = extract_grouped_data_closest_date(data, year)
    percent = safe_parse_float(percent, 100) / 100
    logger.debug('organic weight, country=%s, year=%s, percent=%s', country_id, year, percent)
    return percent


def _irrigated_weight(country_id: str, year: int):
    lookup = download_lookup('region-irrigated.csv', True)
    irrigated_data = get_table_value(lookup, 'termid', country_id, column_name('irrigatedValue'))
    irrigated = extract_grouped_data_closest_date(irrigated_data, year)
    area_data = get_table_value(lookup, 'termid', country_id, column_name('totalCroplandArea'))
    area = extract_grouped_data_closest_date(area_data, year)
    percent = safe_parse_float(irrigated, 1) / safe_parse_float(area, 1)
    logger.debug('irrigated weight, country=%s, year=%s, percent=%s', country_id, year, percent)
    return percent


def _weighted_value(country_id: str, year: int):
    def apply(node: dict):
        organic_weight = _organic_weight(country_id, year)
        irrigated_weight = _irrigated_weight(country_id, year)
        weight = (
            organic_weight if node.get('organic', False) else 1-organic_weight
        ) * (
            irrigated_weight if node.get('irrigated', False) else 1-irrigated_weight
        )
        value = node.get('value')
        return (list_sum(value, value), weight) if value is not None else None
    return apply


def _aggregate_weighted(country_id: str, year: int, term: dict, nodes: list, product: dict):
    values = non_empty_list(map(_weighted_value(country_id, year), nodes))
    weighted_value = [value * weight for value, weight in values]
    value = sum(weighted_value)
    percent = sum(weight for _v, weight in values)
    value = value / percent if percent != 0 else value
    logger.debug('product=%s, country=%s, year=%s, term: %s, value: %s',
                 product.get('@id'), country_id, str(year), term.get('@id'), str(value))
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
        first_node = data.get('nodes', [])[0]
        country_id = first_node.get('country').get('@id')
        year = _end_date_year(first_node)

        def aggregate(term_id: str):
            nodes = data.get(aggregate_key).get(term_id)
            term = nodes[0].get('term')
            return _aggregate_weighted(country_id, year, term, nodes, product)

        aggregates = flatten(map(aggregate, data.get(aggregate_key, {}).keys()))
        return (aggregates, data) if len(aggregates) > 0 else ([], {})

    def aggregate_multiple(data: dict):
        return reduce(
            lambda prev, curr: {**prev, curr: _aggregate_nodes(curr)(data)}, aggregate_key, {}
        )

    return aggregate if isinstance(aggregate_key, str) else aggregate_multiple


def aggregate(aggregate_key: str, groups: dict) -> list:
    return non_empty_list(map(_aggregate_nodes(aggregate_key), groups.values()))
