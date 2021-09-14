from typing import Any, Union
from pydantic import BaseModel
import requests

from .dataclasses.agreement import (
    CancelAgreementRequest,
    CancelAgreementResponse,
    CreateAgreementRequest,
    CreateAgreementResponse,
    ExecuteAgreementRequest,
    ExecuteAgreementResponse,
    QueryAgreementRequest,
    QueryAgreementResponse,
)

from .dataclasses.checkout import (
    CapturePaymentResponse,
    CreatePaymentRequest,
    CreatePaymentResponse,
    CreateTokenizedPaymentRequest,
    CreateTokenizedPaymentResponse,
    ExecutePaymentRequest,
    ExecutePaymentResponse,
    ExecuteTokenizedPaymentResponse,
    QueryPaymentRequest,
    QueryPaymentResponse,
    QueryTokenizedPaymentResponse,
    SearchTokenizedTransactionResponse,
    SearchTransactionDetailsRequest,
    SearchTransactionResponse,
    VoidPaymentResponse,
)
from .dataclasses.base import (
    ClientTypeEnum,
    ErrorResponse,
    TokenCredentials,
    Credential,
)
from .dataclasses.refund import (
    RefundResponse,
    RefundRequest,
    RefundStatusRequest,
    RefundStatusResponse,
)


class BaseAPIClient:
    _default_header = {"Content-Type": "application/json", "Accept": "application/json"}
    _version = None
    _service = None
    _auth = None
    _sandbox = True

    @property
    def _API_ROOT(self):
        return f"https://{self._service}.{'sandbox' if self._sandbox else 'pay'}.bka.sh/v{self._version}/{self._service}"

    @property
    def _ENDPOINTS(self):
        return {
            "grant_token": "",
            "refresh_token": "",
            "create_payment": "",
            "execute_payment": "",
            "query_payment": "",
            "search_transaction": "",
            "refund": "",
            "refund_status": "",
        }

    def __init__(
        self,
        credentials: Credential,
        sandbox: bool = True,
        version: str = "1.2.0-beta",
    ):
        self.credentials = credentials
        self._version = version
        self._sandbox = sandbox

    def _get_auth(self):
        if self._auth:
            self.refresh_token()
            return self._auth
        else:
            self.authenticate()
            return self._auth

    def _get_auth_header(self):
        auth = self._get_auth()
        if not auth:
            return None
        else:
            return {
                "Authorization": auth.id_token,
                "X-App-Key": self.credentials.app_key,
            }

    @staticmethod
    def _validate(data: Any, expected_class: BaseModel):
        if not isinstance(data, expected_class):
            return expected_class.parse_obj(data)
        else:
            return data

    @staticmethod
    def _handle_response(response, success_class):
        resp = response.json()

        if resp.get("errorCode", False):
            return ErrorResponse.parse_obj(resp)

        try:
            return success_class.parse_obj(resp)
        except Exception as e:
            raise e

    def _perform_request(self, data, endpoint=None, url=None, method="post"):
        if not url:
            url = self._ENDPOINTS[endpoint]
        auth_header = self._get_auth_header()
        response = requests.__dict__[method](
            url,
            data,
            headers={
                **auth_header,
                **self._default_header,
            },
        )
        return response

    def authenticate(self):
        response = requests.post(
            self._ENDPOINTS["grant_token"],
            json={
                "app_key": self.credentials.app_key,
                "app_secret": self.credentials.app_secret,
            },
            headers={
                "username": self.credentials.username,
                "password": self.credentials.password,
                **self._default_header,
            },
        )

        if response:
            data = response.json()
            try:
                self._auth = TokenCredentials(**data)
            except Exception as e:
                raise e
        else:
            raise Exception(response.text)

    def refresh_token(self):
        response = requests.post(
            self._ENDPOINTS["grant_token"],
            json={
                "app_key": self.credentials.app_key,
                "app_secret": self.credentials.app_secret,
                "refresh_token": self._auth.refresh_token,
            },
            headers={
                "username": self.credentials.username,
                "password": self.credentials.password,
                **self._default_header,
            },
        )

        if response:
            data = response.json()
            try:
                self._auth = TokenCredentials(**data)
            except Exception as e:
                raise e
        else:
            raise Exception(response.text)


class RefundMixin:
    def refund(self, data: Union[RefundRequest, dict]):
        data = self._validate(data, RefundRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="refund"
            )
            return self._handle_response(response, RefundResponse)
        else:
            raise Exception("Invalid Payload")

    def refund_status(self, data: Union[RefundStatusRequest, dict]):
        data = self._validate(data, RefundStatusRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="refund"
            )
            return self._handle_response(response, RefundStatusResponse)
        else:
            raise Exception("Invalid Payload")


class BasePaymentClient(BaseAPIClient):
    _service = "checkout"

    @property
    def _ENDPOINTS(self):
        return {
            "grant_token": f"{self._API_ROOT}/token/grant",
            "refresh_token": f"{self._API_ROOT}/token/refresh",
            "create_payment": f"{self._API_ROOT}/payment/create",
            "execute_payment": f"{self._API_ROOT}/payment/execute",
            "query_payment": f"{self._API_ROOT}/payment/query",
            "search_transaction": f"{self._API_ROOT}/payment/search",
            "refund": f"{self._API_ROOT}/payment/refund",
            "refund_status": f"{self._API_ROOT}/payment/refund",
        }

    def create_payment(self, data=Union[CreatePaymentRequest, dict]):
        data = self._validate(data, CreatePaymentRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="create_payment"
            )
            return self._handle_response(response, CreatePaymentResponse)
        else:
            raise Exception("Invalid Payload")

    def execute_payment(self, paymentID: str):
        if paymentID:
            response = self._perform_request(
                {}, url=f"{self._ENDPOINTS['execute_payment']}/{paymentID}"
            )
            return self._handle_response(response, ExecutePaymentResponse)
        else:
            raise Exception("Invalid PaymentID")

    def query_payment(self, paymentID: str):
        if paymentID:
            response = self._perform_request(
                {}, url=f"{self._ENDPOINTS['query_payment']}/{paymentID}", method="get"
            )
            return self._handle_response(response, QueryPaymentResponse)
        else:
            raise Exception("Invalid PaymentID")

    def search_transaction(self, trxID: str):
        if trxID:
            response = self._perform_request(
                {},
                url=f"{self._ENDPOINTS['search_transaction']}/{trxID}",
                method="get"
            )
            print(response.text)
            return self._handle_response(response, SearchTransactionResponse)
        else:
            raise Exception("Invalid trxID")


class BKashIFrameClient(RefundMixin, BasePaymentClient):
    pass


class BKashAuthorizedPaymentClient(BasePaymentClient):
    @property
    def _ENDPOINTS(self):
        endpoints = super()._ENDPOINTS
        endpoints["capture"] = f"{self._API_ROOT}/payment/capture"
        endpoints["capture"] = f"{self._API_ROOT}/payment/void"
        return endpoints

    def capture(self, paymentID: str):
        if paymentID:
            response = self._perform_request(
                {}, url=f"{self._ENDPOINTS['capture']}/{paymentID}"
            )
            return self._handle_response(response, CapturePaymentResponse)
        else:
            raise Exception("Invalid PaymentID")

    def void(self, paymentID: str):
        if paymentID:
            response = self._perform_request(
                {}, url=f"{self._ENDPOINTS['void']}/{paymentID}", method="get"
            )
            return self._handle_response(response, VoidPaymentResponse)
        else:
            raise Exception("Invalid PaymentID")


class BKashURLClient(BaseAPIClient, RefundMixin):
    _service = "tokenized"

    @property
    def _ENDPOINTS(self):
        return {
            "grant_token": f"{self._API_ROOT}/checkout/token/grant",
            "refresh_token": f"{self._API_ROOT}/checkout/token/refresh",
            "create_payment": f"{self._API_ROOT}/checkout/create",
            "execute_payment": f"{self._API_ROOT}/checkout/execute",
            "query_payment": f"{self._API_ROOT}/checkout/payment/status",
            "search_transaction": f"{self._API_ROOT}/checkout/general/searchTransaction",
            "refund": f"{self._API_ROOT}/checkout/payment/refund",
            "refund_status": f"{self._API_ROOT}/checkout/payment/refund",
        }

    def create_payment(self, data=Union[CreateTokenizedPaymentRequest, dict]):
        data = self._validate(data, CreateTokenizedPaymentRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="create_payment"
            )
            return self._handle_response(response, CreateTokenizedPaymentResponse)
        else:
            raise Exception("Invalid Payload")

    def execute_payment(self, data=Union[ExecutePaymentRequest, dict]):
        data = self._validate(data, ExecutePaymentRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="execute_payment"
            )

            return self._handle_response(response, ExecuteTokenizedPaymentResponse)
        else:
            raise Exception("Invalid Payload")

    def query_payment(self, data=Union[QueryPaymentRequest, dict]):
        data = self._validate(data, QueryPaymentRequest)
        if data:
            response = response = self._perform_request(
                data.json(exclude_none=True), endpoint="query_payment"
            )
            return self._handle_response(response, QueryTokenizedPaymentResponse)
        else:
            raise Exception("Invalid Payload")

    def search_transaction(self, data=Union[SearchTransactionDetailsRequest, dict]):
        data = self._validate(data, SearchTransactionDetailsRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="search_transaction"
            )
            return self._handle_response(response, SearchTokenizedTransactionResponse)
        else:
            raise Exception("Invalid Payload")


class BKashTokenizedPaymentClient(BKashURLClient):
    @property
    def _ENDPOINTS(self):
        endpoints = super()._ENDPOINTS
        endpoints["query_agreement"] = f"{self._API_ROOT}/checkout/agreement/status"
        endpoints["cancel_agreement"] = f"{self._API_ROOT}/checkout/agreement/cancel"
        return endpoints

    def create_agreement(self, data=Union[CreateAgreementRequest, dict]):
        data = self._validate(data, CreateAgreementRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="create_payment"
            )
            return self._handle_response(response, CreateAgreementResponse)
        else:
            raise Exception("Invalid Payload")

    def execute_agreement(self, data=Union[ExecuteAgreementRequest, dict]):
        data = self._validate(data, ExecuteAgreementRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="create_payment"
            )
            return self._handle_response(response, ExecuteAgreementResponse)
        else:
            raise Exception("Invalid Payload")

    def query_agreement(self, data=Union[QueryAgreementRequest, dict]):
        data = self._validate(data, QueryAgreementRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="query_agreement"
            )
            return self._handle_response(response, QueryAgreementResponse)
        else:
            raise Exception("Invalid Payload")

    def cancel_agreement(self, data=Union[CancelAgreementRequest, dict]):
        data = self._validate(data, CancelAgreementRequest)
        if data:
            response = self._perform_request(
                data.json(exclude_none=True), endpoint="cancel_agreement"
            )
            return self._handle_response(response, CancelAgreementResponse)
        else:
            raise Exception("Invalid Payload")


def get_client(
    credentials: Union[Credential],
    type: ClientTypeEnum,
    sandbox: bool = True,
    version: str = "1.2.0-beta",
):
    client = None
    if type == ClientTypeEnum.IFRAME_BASED:
        client = BKashIFrameClient
    elif type == ClientTypeEnum.URL_BASED:
        client = BKashURLClient
    elif type == ClientTypeEnum.TOKENIZED:
        client = BKashTokenizedPaymentClient
    elif type == ClientTypeEnum.AUTH_AND_CAPTURE:
        client = BKashAuthorizedPaymentClient
    else:
        raise Exception("Invalid Client Type.")

    if not isinstance(credentials, Credential):
        credentials = Credential.parse_obj(credentials)

    return client(credentials, sandbox=sandbox, version=version)
