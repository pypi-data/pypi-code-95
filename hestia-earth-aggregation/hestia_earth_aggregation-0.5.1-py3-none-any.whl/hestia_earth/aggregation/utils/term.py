import re
from hestia_earth.utils.model import linked_node
from unidecode import unidecode
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import find_node, find_node_exact
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

SEARCH_LIMIT = 10000
DEFAULT_REGION_ID = 'region-world'
DEFAULT_COUNTRY_NAME = 'World'


def _fetch_all(term_type: TermTermType): return find_node(SchemaType.TERM, {'termType': term_type.value}, SEARCH_LIMIT)


def _fetch_single(term_name: str): return find_node_exact(SchemaType.TERM, {'name': term_name})


def _fetch_default_country(): return _fetch_single(DEFAULT_COUNTRY_NAME)


def _format_country_name(name: str):
    return re.sub(r'[\(\)\,\.\'\"]', '', unidecode(name).lower().replace(' ', '-')) if name else None


def _is_global(country_name: str): return country_name is None or country_name == DEFAULT_COUNTRY_NAME


def _should_aggregate(term: dict):
    lookup = download_lookup(f"{term.get('termType')}.csv", True)
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('skipAggregation'))
    return True if value is None or value == '' else not value


def _group_by_term_id(group: dict, node: dict):
    term = node.get('term', {})
    term_id = term.get('@id')
    if _should_aggregate(term):
        if term_id not in group:
            group[term_id] = []
        group[term_id].append(node)
    return group


def _update_country(country_name: str):
    return linked_node({
        **(_fetch_single(country_name) if isinstance(country_name, str) else country_name),
        '@type': SchemaType.TERM.value
    })
