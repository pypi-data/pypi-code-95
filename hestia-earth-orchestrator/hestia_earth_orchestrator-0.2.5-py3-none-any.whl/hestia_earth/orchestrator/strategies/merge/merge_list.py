import pydash

from hestia_earth.orchestrator.utils import _non_empty_list, update_node_version
from .merge_node import merge as merge_node

# TODO: use `uniqueArrayItem` from the schema to get the keys for the field
_BLANK_NODE_MATCH_PROPERTIES = [
    'term.@id',
    'operation.@id',
    'startDate',
    'endDate',
    'depthUpper',
    'depthLower'
]


def _match_el(source: dict, dest: dict, same_methodModel: bool):
    def match(key):
        dest_value = pydash.objects.get(dest, key)
        return dest_value is None or dest_value == pydash.objects.get(source, key)

    return all([match(key) for key in _BLANK_NODE_MATCH_PROPERTIES + (['methodModel'] if same_methodModel else [])])


def _find_match_el_index(values: list, el: str, same_methodModel: bool = False):
    return next((i for i in range(len(values)) if _match_el(values[i], el, same_methodModel)), None)


def merge(source: list, dest: list, version: str, args: dict = {}):
    source = source if source is not None else []
    # only merge node if it has the same `methodModel`
    same_methodModel = args.get('sameMethodModel', False)
    for el in _non_empty_list(dest):
        source_index = _find_match_el_index(source, el, same_methodModel)
        if source_index is None:
            source.append(update_node_version(version, el))
        else:
            source[source_index] = merge_node(source[source_index], el, version, args)
    return source
