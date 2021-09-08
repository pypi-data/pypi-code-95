# build-in imports
from dataclasses 	import dataclass
from typing 		import List

# external imports
import requests
from loguru import logger

# project imports
from .models.product	import HubProduct
from .utils				import Environment
from napplib.utils		import AttemptRequests
from napplib.utils		import unpack_payload_dict
from napplib.utils		import LoggerSettings


@logger.catch()
@dataclass
class HubController:
	"""[This controller has the function to execute the calls inside the Napp HUB V2.
		All functions will return a requests.Response.]

	Args:
		environment	(Environment): [The environment for making requests.].
		token 		(str): [The Authorization Token.].
		debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If the environment is not valid, it will raise a TypeError.]
	"""
	environment	: Environment
	token		: str
	debug		: bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.environment, Environment):
			raise TypeError(f'please enter a valid environment. environment: {self.environment}')
		self.headers = {
			'Authorization': f'Bearer {self.token}'
		}

	@AttemptRequests(success_codes=[200])
	def get_sku_by_id(self, sku: str):
		return requests.get(f'{self.environment.value}/skus/{sku}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def put_products(self, products: List[HubProduct], seller_id: int):
		return requests.put(f'{self.environment.value}/sellers/{seller_id}/skus/bulk', headers=self.headers, data=unpack_payload_dict(products))
