import os

from moosetools.test.test_connect import scenarios

free_dictionary_api_connect_string = {
    "base_url": "https://api.dictionaryapi.dev/api/v1/"
}
words_api_connect_string = {
    "base_url": "https://wordsapiv0.p.rapidapi.com/words/",
    "session_headers": {
        'x-rapidapi-host': os.getenv('moosetools_x_rapidapi_host'),
        'x-rapidapi-key': os.getenv('moosetools_x_rapidapi_key')
    }}

gorest_api_connect_string = {
    "base_url": "https://gorest.co.in/public/v0/",
    "session_headers": {'Authorization': f'Bearer {os.getenv("moosetools_gorest_token")}'},
    "session_keys": []
}


# def pytest_addoption(parser):
#     parser.addoption("--scenario", action="store", type=str, default='free_dictionary_api',
#                      help=f'scenario to test: {scenarios.keys()}')


# def pytest_generate_tests(metafunc):
#     if "scenario_name" in metafunc.fixturenames:
#         metafunc.parametrize("scenario_name", metafunc.config.getoption("scenario"))


