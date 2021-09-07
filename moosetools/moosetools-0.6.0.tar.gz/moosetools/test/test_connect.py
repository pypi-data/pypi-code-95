import os

import pytest

from moosetools.connect import connect_json_app, _default_store_, __app__

scenarios = {
    'free_dictionary_api': {
        "connect": {"base_url": "https://api.dictionaryapi.dev/api/v2/"},
        "get": [
            {"url": 'entries/en/monkey'},
            {"url": '/entries/en/monkey'}
        ]
    },
    'words_api': {
        'connect': {
            "base_url": "https://wordsapiv1.p.rapidapi.com/words/",
            "session_headers": {
                'x-rapidapi-host': f'{os.getenv("moosetools_x_rapidapi_host")}',
                'x-rapidapi-key': f'{os.getenv("moosetools_x_rapidapi_key")}'
            }
        },
        "get": [
            {"url": 'incredible/definitions'},
            {"url": 'factory/synonyms'}
        ]
    },
    'gorest_api': {
        'connect': {
            "base_url": "https://gorest.co.in/public/v1/",
            "session_headers": {'Authorization': f'Bearer {os.getenv("moosetools_gorest_token")}'},
        },
        'get': [
            {'url': '/users'},
            {'url': '/users', 'params': {'page': '1'}}
        ]
    }
}


@pytest.fixture(params=scenarios.keys())
def scenario(request):
    return scenarios.get(request.param)


@pytest.fixture
def connect(scenario):
    return connect_json_app(**scenario['connect'])


def test_connect_json_app(connect, scenario):
    assert connect.base_url == scenario['connect']['base_url']
    assert connect.store == _default_store_
    assert connect.session_store == os.path.join(connect.store, f'.{__app__}.session')


def test_connect_json_app_get(connect, scenario):
    for api in scenario.get('get'):
        print(api)
        _resp = connect.get(**api)
        assert _resp.ok is True
        assert _resp.status_code == 200
