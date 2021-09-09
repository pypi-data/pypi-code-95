from functools import reduce
import pydash

from hestia_earth.orchestrator.utils import _non_empty, _non_empty_list, update_node_version
from . import merge_default
from . import merge_list
from . import merge_node


def _non_empty_results(results: list):
    return list(filter(lambda value: _non_empty(value) and _non_empty_list(value.get('result')), results))


def _merge_version(data: dict): return data.get('version')  # set as a function to patch it for testing


_STRATEGIES = {
    'list': merge_list.merge,
    'node': merge_node.merge,
    'default': merge_default.merge
}


def _merge_result(data: dict, result: dict):
    key = result.get('model').get('key')
    values = result.get('result')
    version = _merge_version(result)
    merge_type = result.get('model').get('mergeStrategy', 'default')
    merge_args = result.get('model').get('mergeArgs', {})
    current = data.get(key)
    values = [values] if not isinstance(values, list) and merge_type == 'list' else values
    new_value = _STRATEGIES[merge_type](current, values, version, merge_args)
    new_data = pydash.objects.merge({}, data, {key: new_value})
    return update_node_version(version, new_data, data)


def merge(data: dict, results: list):
    return reduce(_merge_result, _non_empty_results(results), data)
