import requests
import sys

from http import HTTPStatus
from slai.clients.identity import get_identity_client
from slai.modules.parameters import from_config
from slai.modules.runtime import detect_credentials, detect_runtime, ValidRuntimes
from slai.exceptions import (
    InvalidNotebookAuthToken,
    InvalidCredentials,
)

from getpass import getpass


class Login:
    APP_BASE_URL = from_config(
        key="APP_BASE_URL",
        default="https://beta.slai.io",
    )

    def __init__(self, *, client_id=None, client_secret=None, key_type=None):
        self.identity_client = get_identity_client(
            client_id=client_id, client_secret=client_secret, key_type=key_type
        )

        if client_id is None or client_secret is None:
            self._notebook_auth_flow()
        else:
            self.client_id = client_id
            self.client_secret = client_secret

        self._validate_credentials()

    def _validate_credentials(self):
        try:
            _ = self.identity_client.validate_credentials()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.BAD_REQUEST:
                if e.response.json()["detail"][0] == "invalid_key_type":
                    raise InvalidCredentials("invalid_key_type")

            raise InvalidCredentials("invalid_credentials")

        # cache credentials on slai module
        setattr(
            sys.modules["slai"],
            "credentials",
            {"client_id": self.client_id, "client_secret": self.client_secret},
        )

        setattr(
            sys.modules["slai"],
            "authenticated",
            True,
        )

        print("logged in successfully.")

    def _notebook_auth_flow(self):
        runtime = detect_runtime()

        if runtime == ValidRuntimes.LocalNotebook:
            credentials = detect_credentials(runtime=runtime)
            self.client_id = credentials["client_id"]
            self.client_secret = credentials["client_secret"]
        else:
            token = getpass(
                f"navigate to {self.APP_BASE_URL}/notebook-auth for a temporary login token: "
            )

            try:
                response = self.identity_client.validate_notebook_auth_token(
                    token=token
                )
            except requests.exceptions.HTTPError:
                raise InvalidNotebookAuthToken("invalid_token")

            self.client_id = response["client_id"]
            self.client_secret = response["client_secret"]

        self.identity_client.client_id = self.client_id
        self.identity_client.client_secret = self.client_secret
        self.identity_client.credentials_loaded = True
