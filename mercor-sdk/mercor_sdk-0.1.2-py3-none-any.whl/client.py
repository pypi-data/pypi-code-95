import abc
import os
from typing import Optional

import backoff
import requests

from mercor_sdk.datatypes.balance import AlgorithmBalanceResponse
from mercor_sdk.datatypes.client import ClientRequest, ClientToken
from mercor_sdk.datatypes.status import TradeStatusResponse
from mercor_sdk.datatypes.ticker import TickerListResponse, TickerResponse
from mercor_sdk.datatypes.trade import TradeRequestResponse
from mercor_sdk.tokens import CryptoToken

API_URL = "https://api.mercor.finance/api/v1"

REQUEST_RETRIES = 3
REQUEST_TIMEOUT = 60
REQUEST_STATUS_TIMEOUT = 60


class ClientSession(abc.ABC):
    def __init__(self, api_url: str = os.getenv("API_URL", API_URL)) -> None:
        self.api_url = api_url

    @abc.abstractmethod
    def get(self, request: ClientRequest) -> dict:
        pass

    @abc.abstractmethod
    def post(self, request: ClientRequest) -> dict:
        pass


class WebClientSession(ClientSession):
    def __init__(self, timeout: float = REQUEST_TIMEOUT) -> None:
        super().__init__()
        self.timeout = timeout
        self.session = requests.Session()

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_tries=REQUEST_RETRIES,
    )
    def get(self, request: ClientRequest) -> dict:
        response = self.session.get(self.api_url + request.endpoint, timeout=self.timeout, **request.payload)
        response.raise_for_status()

        return response.json()

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_tries=REQUEST_RETRIES,
    )
    def post(self, request: ClientRequest) -> dict:
        response = self.session.post(self.api_url + request.endpoint, timeout=self.timeout, **request.payload)
        response.raise_for_status()

        return response.json()


class InMemoryClientSession(ClientSession):
    def __init__(self) -> None:
        super().__init__()
        self.response: dict = {}

    def get(self, request: ClientRequest) -> dict:
        return self.response

    def post(self, request: ClientRequest) -> dict:
        return self.response


class MercorClient:
    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession = WebClientSession(),
        token: Optional[ClientToken] = None,
    ) -> None:
        self.username = username
        self.password = password
        self.session = session
        self.token = token

    def __getattr__(self, name):
        try:
            return self.session.__getattribute__(name)
        except AttributeError:
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} username={self.username!r} password={self.password!r} token={self.token!r}>"

    @property
    def public_address(self) -> str:
        return self.username

    @property
    def access_token(self) -> str:
        if self.token is None or self.token.is_expired():
            headers = _create_login_header()
            payload = _create_login_payload(self.username, self.password)
            request = ClientRequest(endpoint="/login", headers=headers, data=payload)
            self.token = ClientToken.parse_obj(self.post(request))

        return self.token.access_token

    def buy(self, slippage: float, relative_amount: float) -> TradeRequestResponse:
        headers = _create_access_header(self.access_token)
        payload = _create_trade_payload(self.public_address, slippage, relative_amount)
        request = ClientRequest(endpoint="/buy", headers=headers, json_data=payload)

        return TradeRequestResponse(response=self.post(request))

    def sell(self, slippage: float, relative_amount: float) -> TradeRequestResponse:
        headers = _create_access_header(self.access_token)
        payload = _create_trade_payload(self.public_address, slippage, relative_amount)
        request = ClientRequest(endpoint="/sell", headers=headers, json_data=payload)

        return TradeRequestResponse(response=self.post(request))

    def status(self, transaction_hash: str, timeout_in_seconds: int = REQUEST_STATUS_TIMEOUT) -> TradeStatusResponse:
        headers = _create_access_header(self.access_token)
        payload = _create_status_payload(self.public_address, transaction_hash, timeout_in_seconds)
        request = ClientRequest(endpoint="/status", headers=headers, json_data=payload)

        return TradeStatusResponse(response=self.post(request))

    def balance(self) -> AlgorithmBalanceResponse:
        headers = _create_access_header(self.access_token)
        request = ClientRequest(endpoint="/balance", headers=headers)

        return AlgorithmBalanceResponse(response=self.get(request))

    def ticker(self, crypto_token: CryptoToken) -> TickerResponse:
        headers = _create_access_header(self.access_token)
        request = ClientRequest(endpoint="/ticker/" + crypto_token, headers=headers)

        return TickerResponse(response=self.get(request))

    def ticker_list(self) -> TickerListResponse:
        headers = _create_access_header(self.access_token)
        request = ClientRequest(endpoint="/ticker/", headers=headers)

        return TickerListResponse(response=self.get(request))


def _create_access_header(access_token: str) -> dict:
    return {"Authorization": f"bearer {access_token}"}


def _create_login_header() -> dict:
    return {"Content-type": "application/x-www-form-urlencoded"}


def _create_login_payload(username: str, password: str) -> dict:
    return {"grant_type": "password", "username": username, "password": password}


def _create_trade_payload(public_address: str, slippage: float, relative_amount: float) -> dict:
    return {
        "trade": {
            "algorithm_id": {
                "public_address": public_address,
            },
            "slippage": {
                "amount": slippage,
            },
            "relative_amount": relative_amount,
        },
    }


def _create_status_payload(public_address: str, transaction_hash: str, timeout_in_seconds: int) -> dict:
    return {
        "algorithm_id": {
            "public_address": public_address,
        },
        "transaction_hash": {
            "value": transaction_hash,
        },
        "timeout_in_seconds": timeout_in_seconds,
    }
