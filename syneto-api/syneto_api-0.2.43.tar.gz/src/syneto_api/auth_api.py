import os
from .api_client import APIClientBase
from .keyring import KeyRing
import urllib.parse


class Authentication(APIClientBase):
    def __init__(self, url_base=None, **kwargs):
        super().__init__(url_base or os.environ.get("AUTHORIZATION_SERVICE", ""), **kwargs)

    def on_login_response(self, response):
        if "jwt" in response:
            token = response["jwt"]
            parsed_base_url = urllib.parse.urlparse(self.url_base)
            keyring = KeyRing(parsed_base_url.netloc)
            keyring.set_token(token)
        return response

    def login(self, username: str, password: str):
        body = {"username": username, "password": password}
        return self.post_request("/login", body=body, on_response_callback=self.on_login_response)

    def get_public_key(self, username: str):
        return self.get_request("/public-key", query_args={"username": username})

    def add_authorized_key(self, username: str, public_key: str):
        return self.post_request("/authorized-keys", query_args={"username": username}, body={"public_key": public_key})

    def remove_authorized_key(self, username: str, public_key: str):
        return self.delete_request(
            "/authorized-keys",
            query_args={"username": username},
            body={"public_key": public_key},
        )
