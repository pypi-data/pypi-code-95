from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value
from hestia_earth.utils.model import filter_list_term_type


def get_lookup_factor(practices: list, lookup_col: str):
    practices = filter_list_term_type(practices, TermTermType.EXCRETAMANAGEMENT)
    practice_id = practices[0].get('term', {}).get('@id') if len(practices) > 0 else None
    lookup = download_lookup(f"{TermTermType.EXCRETAMANAGEMENT.value}.csv")
    return get_table_value(lookup, 'termid', practice_id, column_name(lookup_col))
