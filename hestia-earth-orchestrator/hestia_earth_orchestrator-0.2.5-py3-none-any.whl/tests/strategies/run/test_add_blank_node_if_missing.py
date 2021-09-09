from unittest.mock import patch

from hestia_earth.orchestrator.strategies.run.add_blank_node_if_missing import should_run

class_path = 'hestia_earth.orchestrator.strategies.run.add_blank_node_if_missing'


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run(mock_node_exists, *args):
    data = {}
    model = {}

    # node does not exists => run
    mock_node_exists.return_value = None
    assert should_run(data, model) is True

    # node exists + no params => no run
    node = {}
    mock_node_exists.return_value = node
    assert not should_run(data, model)


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run_non_reliable(mock_node_exists, *args):
    data = {}
    node = {}
    mock_node_exists.return_value = node
    model = {'runArgs': {'runNonReliable': True}}

    # node is reliable => no run
    node['reliability'] = 2
    assert not should_run(data, model)

    # node is not reliable => run
    node['reliability'] = 3
    assert should_run(data, model) is True


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run_non_added_term(mock_node_exists, *args):
    data = {}
    node = {}
    mock_node_exists.return_value = node
    model = {'runArgs': {'runNonAddedTerm': True}}

    # term has been added => no run
    node['added'] = ['term']
    assert not should_run(data, model)

    # term has not been added => run
    node['added'] = []
    assert should_run(data, model) is True


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run_non_measured(mock_node_exists, *args):
    data = {}
    node = {}
    mock_node_exists.return_value = node
    model = {'runArgs': {'runNonMeasured': True}}

    # term measured => no run
    node['methodTier'] = 'measured'
    assert not should_run(data, model)

    # term not measured => run
    node['methodTier'] = 'background'
    assert should_run(data, model) is True
