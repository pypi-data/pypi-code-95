from unittest.mock import patch
import pytest
from hestia_earth.schema import NodeType

from tests.utils import SOURCE, WORLD
from hestia_earth.aggregation import aggregate, _aggregate_by_timerange

class_path = 'hestia_earth.aggregation'
country_name = 'Japan'
node_type = NodeType.IMPACTASSESSMENT.value
time_range = (2000, 2009)


@patch(f"{class_path}._fetch_single", return_value={'@id': 'single'})
@patch(f"{class_path}._fetch_default_country", return_value=WORLD)
@patch(f"{class_path}._get_source", return_value=SOURCE)
@patch(f"{class_path}.get_time_ranges", return_value=[time_range])
@patch(f"{class_path}.earliest_date", return_value='')
@patch(f"{class_path}._aggregate_by_timerange")
def test_aggregate(mock_aggregate, *args):
    # aggregate by country
    aggregate(node_type, country_name)
    mock_aggregate.assert_called_once_with(node_type, {'@id': 'single'}, SOURCE)

    mock_aggregate.reset_mock()

    # aggregate global
    aggregate(node_type)
    mock_aggregate.assert_called_once_with(node_type, WORLD, SOURCE)


@patch(f"{class_path}.get_time_ranges", return_value=[time_range])
@patch(f"{class_path}.earliest_date", return_value='')
@patch(f"{class_path}._fetch_single", return_value=None)
def test_aggregate_country_not_found(*args):
    with pytest.raises(Exception):
        aggregate(node_type, country_name)


@patch(f"{class_path}.find_nodes", return_value=[])
@patch(f"{class_path}._call_aggregate_by_type", return_value=[])
def test_aggregate_by_timerange(mock_call_aggregate, *args):
    time_range = (2001, 2010)
    _aggregate_by_timerange(node_type, country={}, source={})(time_range)
    mock_call_aggregate.assert_called_once()
