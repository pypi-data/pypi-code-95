import ujson
import requests

from tests.api.base import get_api, get_headers

ENDPOINT = 'info'


class TestInfoMethods:
    def test_post_status_code_without_token(self):
        response = requests.get(get_api(ENDPOINT), timeout=300)
        assert response.status_code == 400

    def test_post_status_code_with_token(self):
        response = requests.post(get_api(ENDPOINT), headers=get_headers(), timeout=300)
        res = ujson.dumps(response.text)

        assert response.status_code == 201, "Bad request"
        assert len(res["countries"]) > 0, "There is no countries"
        assert len(res["languages"]) > 0, "There is no languages"
