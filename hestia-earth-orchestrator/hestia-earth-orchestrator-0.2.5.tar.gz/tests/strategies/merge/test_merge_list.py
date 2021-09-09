from unittest.mock import patch
import pydash

from hestia_earth.orchestrator.strategies.merge.merge_list import merge

class_path = 'hestia_earth.orchestrator.strategies.merge.merge_list'


@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_new_node(*args):
    old_node = {
        'term': {'@id': 'old-term'},
        'value': 1
    }
    new_node = {
        'term': {'@id': 'new-term'},
        'value': 2
    }
    result = merge([old_node], [new_node], '1')
    assert result == [old_node, new_node]


@patch(f"{class_path}.merge_node", side_effect=lambda a, b, *args: pydash.objects.merge({}, a, b))
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_existing_node(*args):
    old_node = {
        'term': {'@id': 'term'},
        'value': 1
    }
    new_node = {
        **old_node,
        'value': 2
    }
    result = merge([old_node], [new_node], '1')
    assert result == [new_node]

    # with different depths
    old_node['depthUpper'] = 100
    new_node['depthUpper'] = 50
    result = merge([old_node], [new_node], '1')
    assert result == [old_node, new_node]
