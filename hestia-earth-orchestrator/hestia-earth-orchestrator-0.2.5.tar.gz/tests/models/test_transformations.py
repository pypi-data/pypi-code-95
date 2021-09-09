from unittest.mock import patch
import json
import os

from tests.utils import fixtures_path
from hestia_earth.orchestrator.models.transformations import run, _include_practice

folder_path = os.path.join(fixtures_path, 'transformation')


@patch('hestia_earth.orchestrator.strategies.merge._merge_version', return_value='0.0.0')
def test_run(*args):
    with open(os.path.join(folder_path, 'config.json'), encoding='utf-8') as f:
        config = json.load(f)
    with open(os.path.join(folder_path, 'cycle.jsonld'), encoding='utf-8') as f:
        cycle = json.load(f)
    with open(os.path.join(folder_path, 'result.jsonld'), encoding='utf-8') as f:
        expected = json.load(f)

    result = run(config.get('models'), cycle)
    assert result == expected


def test_include_practice():
    term = {'@id': 'genericCropProduct', 'termType': 'crop'}
    assert not _include_practice({'term': term})

    term = {'@id': 'yieldOfPrimaryAquacultureProductLiveweightPerM2', 'termType': 'aquacultureManagement'}
    assert _include_practice({'term': term}) is True
