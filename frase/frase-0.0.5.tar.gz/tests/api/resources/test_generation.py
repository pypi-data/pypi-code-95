import ujson
import requests
import pytest

from tests.api.base import get_api, get_headers

ENDPOINT = 'generation'
data = {
    "query": "Hello world query",
    "lang": "German",
    "country": "Germany",
    "text_length": 1000
}


class TestGenerationMethods:
    def test_post_status_code_without_token(self):
        response = requests.post(get_api(ENDPOINT), ujson.dumps(data), timeout=300)
        assert response.status_code == 400

    def test_post_status_code_with_token(self):
        response = requests.post(get_api(ENDPOINT), ujson.dumps(data), headers=get_headers(), timeout=300)
        res = ujson.loads(response.text)

        assert response.status_code == 201, "Bad request"
        assert type(res["generated_text"]) is str and len(res["generated_text"]) > 0, "There is no generated text"
        assert type(res["generated_text"]) is str and len(
            res["generated_text"]) > 900, "The generated text's length less than should be"
