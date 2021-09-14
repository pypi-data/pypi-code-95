# build-in imports
import sys
from dataclasses import dataclass
from typing import List

# external imports
import requests
from loguru import logger

# project imports
from napplib.utils import AttemptRequests
from napplib.utils import LoggerSettings
from napplib.utils import unpack_payload_dict
from napplib.vtex.v2.models.order import VtexOrderInvoice


@logger.catch(onerror=lambda _: sys.exit(1))
@dataclass
class VtexController:
    account_name: str
    app_key: str
    app_token: str
    environment: str
    debug: bool = False

    def __post_init__(self):
        level = "DEBUG" if self.debug else "INFO"
        LoggerSettings(level=level)

        if not self.account_name:
            raise TypeError("Account name need to be defined")

        if not self.app_key:
            raise TypeError("App key need to be defined")

        if not self.app_token:
            raise TypeError("App token need to be defined")

        if not self.environment:
            self.environment = "vtexcommercestable"

        self.headers = {
            "X-VTEX-API-AppKey": self.app_key,
            "X-VTEX-API-AppToken": self.app_token,
        }

    @AttemptRequests(success_codes=[200, 404])
    def get_order_by_id(self, order_id: str):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        endpoint = f"https://{self.account_name}.{self.environment}.com.br/api/oms/pvt/orders/{order_id}"
        return requests.get(endpoint, headers=headers)

    @AttemptRequests(success_codes=[200])
    def post_invoice(self, order_id: str, invoice: VtexOrderInvoice):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        endpoint = f"https://{self.account_name}.{self.environment}.com.br/api/oms/pvt/orders/{order_id}/invoice"

        return requests.post(endpoint, headers=headers, data=unpack_payload_dict(invoice,remove_null=True))
