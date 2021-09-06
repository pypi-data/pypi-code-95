from unittest.mock import patch, MagicMock

from tests.utils import start_year, end_year
from hestia_earth.aggregation.utils.queries import (
    _download_node, _download_nodes, _query_all_nodes, _country_nodes, _global_nodes, find_nodes
)

class_path = 'hestia_earth.aggregation.utils.queries'
country_name = 'Japan'


class FakePostRequest():
    def __init__(self, results=[]) -> None:
        self.results = results
        pass

    def json(self):
        return {'results': self.results}


@patch(f"{class_path}.download_hestia", return_value={})
def test_download_node(mock_download_hestia):
    _download_node('')({})
    mock_download_hestia.assert_called_once()


@patch(f"{class_path}._download_node")
def test_download_nodes(mock_download):
    mock = MagicMock()
    mock_download.return_value = mock
    nodes = [{}, {}]
    _download_nodes(nodes)
    assert mock.call_count == len(nodes)


@patch('requests.post', return_value=FakePostRequest())
def test_query_all_nodes(mock_post):
    _query_all_nodes('', start_year, end_year, 'Japan')
    mock_post.assert_called_once()


@patch(f"{class_path}._query_all_nodes", return_value=[])
@patch(f"{class_path}._download_nodes", return_value=[])
def test_country_nodes(mock_download, *args):
    _country_nodes('', start_year, end_year, 'Japan')
    mock_download.assert_called_once_with([], data_state='recalculated')


@patch('requests.post', return_value=FakePostRequest())
@patch(f"{class_path}._download_nodes", return_value=[])
def test_global_nodes(mock_download, *args):
    _global_nodes('', start_year, end_year)
    mock_download.assert_called_once_with([])


@patch(f"{class_path}._global_nodes", return_value=[])
@patch(f"{class_path}._country_nodes", return_value=[])
def test_find_nodes(mock_find_country, mock_find_global):
    find_nodes('', 0, 0, 'Japan')
    mock_find_country.assert_called_once()
    mock_find_global.assert_not_called

    find_nodes('', 0, 0, 'World')
    mock_find_global.assert_called_once()
