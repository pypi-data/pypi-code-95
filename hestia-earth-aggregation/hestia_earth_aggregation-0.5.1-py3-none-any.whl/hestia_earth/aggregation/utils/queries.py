import requests
import json
from concurrent.futures import ThreadPoolExecutor
from hestia_earth.schema import NodeType, SCHEMA_VERSION
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.request import api_url

from hestia_earth.aggregation.log import logger
from hestia_earth.aggregation.utils import _save_json
from .term import DEFAULT_COUNTRY_NAME

SEARCH_LIMIT = 10000
# exclude ecoinvent data
EXCLUDE_BIBLIOS = [
    'The ecoinvent database version 3 (part I): overview and methodology'
]
MATCH_AGGREGATED_QUERY = {'match': {'aggregated': 'true'}}
MATCH_SCHEMA_VERSION = {'regexp': {'schemaVersion': f"[{SCHEMA_VERSION.split('.')[0]}][.].*"}}


def _date_range_query(start: int, end: int):
    return {'range': {'endDate': {'gte': str(start), 'lte': str(end)}}} if start and end else None


SOURCE_FIELD_BY_TYPE = {
    NodeType.CYCLE.value: 'defaultSource',
    NodeType.SITE.value: 'defaultSource'
}


def _source_query(node_type: str, title: str):
    source_field = SOURCE_FIELD_BY_TYPE.get(node_type, 'source')
    return {'match': {f"{source_field}.bibliography.title.keyword": title}}


def _node_type_query(node_type: str):
    return {
        'bool': {
            'must': [
                {'match': {'@type': node_type}},
                MATCH_SCHEMA_VERSION
            ],
            'must_not': list(map(lambda title: _source_query(node_type, title), EXCLUDE_BIBLIOS)) + [
                MATCH_AGGREGATED_QUERY
            ]
        }
    }


COUNTRY_FIELD_BY_TYPE = {
    NodeType.CYCLE.value: 'site.country'
}


def _country_query(node_type: str, country_name: str):
    country_field = COUNTRY_FIELD_BY_TYPE.get(node_type, 'country')
    return {'match': {f"{country_field}.name.keyword": country_name}}


def _run_query(data: dict):
    headers = {'Content-Type': 'application/json'}
    params = json.dumps(data)
    logger.debug('Running query: %s', params)
    return requests.post(f'{api_url()}/search', params, headers=headers).json().get('results', [])


def _query_all_nodes(node_type: str, start_year: int, end_year: int, country_name: str):
    query = _node_type_query(node_type)
    date_range = _date_range_query(start_year, end_year)
    query['bool']['must'].extend([date_range] if date_range else [])
    if country_name != DEFAULT_COUNTRY_NAME:
        query['bool']['must'].append(_country_query(node_type, country_name))

    return _run_query({
        'query': query,
        'limit': SEARCH_LIMIT,
        'fields': ['@id', '@type']
    })


def _download_node(data_state=''):
    def download(n):
        try:
            node = download_hestia(n.get('@id'), n.get('@type'), data_state=data_state)
            return node if node.get('@type') else None
        except Exception:
            logger.debug('skip non-%s %s: %s', data_state, n.get('@type'), n.get('@id'))
            return None
    return download


def _download_nodes(nodes: list, data_state=''):
    total = len(nodes)
    with ThreadPoolExecutor() as executor:
        nodes = non_empty_list(executor.map(_download_node(data_state), nodes))
    logger.debug('downloaded %s nodes / %s total nodes', str(len(nodes)), str(total))
    return nodes


def _country_nodes(node_type: str, start_year: int, end_year: int, country_name: str):
    # TODO: paginate search and improve performance
    nodes = _query_all_nodes(node_type, start_year, end_year, country_name)
    return _download_nodes(nodes, data_state='recalculated')


def _global_nodes(node_type: str, start_year: int, end_year: int):
    nodes = _run_query({
        'query': {
            'bool': {
                'must': non_empty_list([
                    {'match': {'@type': node_type}},
                    MATCH_AGGREGATED_QUERY,
                    MATCH_SCHEMA_VERSION,
                    _date_range_query(start_year, end_year)
                ]),
                'must_not': [
                    _country_query(node_type, DEFAULT_COUNTRY_NAME)
                ]
            }
        },
        'limit': SEARCH_LIMIT,
        'fields': ['@id', '@type']
    })
    return _download_nodes(nodes)


def find_nodes(node_type: str, start_year: int, end_year: int, country_name: str):
    nodes = _country_nodes(node_type, start_year, end_year, country_name) if country_name != DEFAULT_COUNTRY_NAME \
        else _global_nodes(node_type, start_year, end_year)
    _save_json({'nodes': nodes}, '-'.join([
        str(v) for v in ['nodes', node_type, country_name, start_year, end_year] if v
    ]))
    return nodes


def earliest_date(node_type: str, country_name: str):
    query = _node_type_query(node_type)
    if country_name and country_name != DEFAULT_COUNTRY_NAME:
        query['bool']['must'].append(_country_query(node_type, country_name))
    params = {
        'query': query,
        'limit': 1,
        'fields': ['endDate'],
        'sort': [{'endDate.keyword': 'asc'}]
    }
    results = _run_query(params)
    return results[0].get('endDate') if len(results) > 0 else None
