import webbrowser
from typing import Optional

import keyring
from oauth2_client.credentials_manager import OAuthError, ServiceInformation
from structlog import get_logger

from .gnista_credential_manager import GnistaCredentialManager

log = get_logger()


class GnistaConnection:
    scope = ["data-api"]

    def __init__(self, base_url: Optional[str]):
        if base_url is None:
            base_url = "https://aws.gnista.io"

        self.base_url = base_url
        self.refresh_token: Optional[str] = None
        self.access_token: Optional[str] = None
        self.id_token: Optional[str] = None
        self.tenant_name: Optional[str] = None

    def __str__(self):
        token_available = self.access_token is not None
        return "Gnista Connection to" + self.base_url + " has token: " + token_available

    def _get_base_url(self) -> str:
        return self.base_url

    def get_access_token(self) -> str:
        if self.refresh_token is None:
            # pylint: disable=E1128
            self.refresh_token = self._load_refresh_token()

        if (self.access_token is None or self.id_token is None) and self.refresh_token is None:
            # Initial create of tokens
            log.info("Starting First Time Login")
            self._create_tokens()
        else:
            # refresh with existing refresh token
            if self.refresh_token is not None:
                try:
                    log.info("Using stored refresh Token to Login")
                    self._refresh_tokens(refresh_token=self.refresh_token)
                except OAuthError:
                    log.info("Error using refresh Token, try getting a new one", exc_info=True)
                    # Initial create of tokens
                    self._create_tokens()

        if self.access_token is None:
            raise Exception("No Token available")
        return self.access_token

    def _get_service_info(self, scope: list = None) -> ServiceInformation:
        if scope is None:
            scope = self.scope

        return ServiceInformation(
            self.base_url + "/authentication/connect/authorize",
            self.base_url + "/authentication/connect/token",
            "python",
            "",
            scope,
            False,
        )

    def _refresh_tokens(self, refresh_token: str):
        service_information = self._get_service_info()
        manager = GnistaCredentialManager(service_information)
        manager.init_with_token(refresh_token)

        self.tenant_name = manager.tenant_name
        self.access_token = manager.access_token
        self.refresh_token = manager.refresh_token
        self.id_token = manager.id_token

    def _create_tokens(self, scope: list = None):
        if scope is None:
            scope = self.scope

        scope.append("openid")
        scope.append("profile")
        scope.append("offline_access")

        service_information = self._get_service_info(scope)

        manager = GnistaCredentialManager(service_information)
        # manager.init_with_client_credentials()
        redirect_uri = "http://localhost:4200/home"
        url = manager.init_authorize_code_process(redirect_uri=redirect_uri, state="myState")
        log.info("Authentication has been started. Please follow the link to authenticate with your user:", url=url)
        webbrowser.open(url)

        code = manager.wait_and_terminate_authorize_code_process()
        # From this point the http server is opened on 8080 port and wait to receive a single GET request
        # All you need to do is open the url and the process will go on
        # (as long you put the host part of your redirect uri in your host file)
        # when the server gets the request with the code (or error) in its query parameters

        manager.init_with_authorize_code(redirect_uri, code)
        # Here access and refresh token may be used with self.refresh_token
        self.tenant_name = manager.tenant_name
        self.access_token = manager.access_token
        self.refresh_token = manager.refresh_token
        self.id_token = manager.id_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _store_refresh_token(self, refresh_token: str):
        pass

    # pylint: disable=R0201
    def _load_refresh_token(self) -> Optional[str]:
        return None


class StaticTokenGnistaConnection(GnistaConnection):
    def __init__(self, base_url: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(base_url=base_url)
        self.refresh_token = refresh_token

    def _store_refresh_token(self, refresh_token: str):
        pass

    def _load_refresh_token(self) -> Optional[str]:
        return self.refresh_token


class KeyringGnistaConnection(GnistaConnection):
    def __init__(
        self,
        service_name: str = "gnista_library",
        base_url: Optional[str] = None,
        enable_store_refresh_token: bool = True,
    ):
        super().__init__(base_url=base_url)
        self.enable_store_refresh_token = enable_store_refresh_token
        self.service_name = service_name

    def _get_token_name(self):
        return "__refresh_token__:" + super()._get_base_url()

    def clear_stored_token(self):
        keyring.delete_password(self.service_name, self._get_token_name())

    def _store_refresh_token(self, refresh_token: str):
        if self.enable_store_refresh_token:
            pass

        keyring.set_password(self.service_name, self._get_token_name(), refresh_token)

    def _load_refresh_token(self) -> Optional[str]:
        token = keyring.get_password(self.service_name, self._get_token_name())
        return token
