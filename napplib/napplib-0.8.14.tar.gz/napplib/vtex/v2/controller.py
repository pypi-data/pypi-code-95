# build-in imports
import sys
from dataclasses import dataclass
from typing import List

# external imports
import requests
from loguru import logger

# project imports
from .models.product import HubProduct
from napplib.utils import AttemptRequests
from napplib.utils import unpack_payload_dict
from napplib.utils import LoggerSettings


@logger.catch(onerror=lambda _: sys.exit(1))
@dataclass
class VtexController:
    """[This controller has the function to execute the calls inside the Napp HUB V2.
            All functions will return a requests.Response.]

    Args:
            environment	(Environment): [The environment for making requests.].
            token 		(str): [The Authorization Token.].
            debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

    Raises:
            TypeError: [If the environment is not valid, it will raise a TypeError.]
    """

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
