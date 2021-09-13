# build-in imports
from dataclasses 	import dataclass
from typing 		import List
from typing 		import Optional

# external imports
import requests
from loguru import logger

# project imports
from .models.product	import HubProduct
from .models.order	    import HubOrder
from .models.channel	import ChannelType
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
	environment				: Environment
	token					: str
	debug					: bool = False
	endpoint_development	: Optional[str] = None

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.environment, Environment):
			raise TypeError(f'please enter a valid environment. environment: {self.environment}')
		self.headers = {
			'Authorization': f'Bearer {self.token}'
		}

	@AttemptRequests(success_codes=[200])
	def get_sku_by_id(self, sku_id: str):
		return requests.get(f'{self.__get_endpoint_base()}/skus/{sku_id}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_price_and_stock_by_external_ids(self, external_seller_id: str, external_channel_id: str, external_sku: str):
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/skus/external/{external_sku}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def put_products(self, products: List[HubProduct], seller_id: int):
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{seller_id}/skus/bulk', headers=self.headers, data=unpack_payload_dict(products,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def put_order(self, external_seller_id: str, external_channel_id: str, order: HubOrder):
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/orders', headers=self.headers, data=unpack_payload_dict(order,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def get_order_by_id(self, order_id: str):
		return requests.get(f'{self.__get_endpoint_base()}/orders/{order_id}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_logistics_shipping_fee(self, seller_id: str, zip_code: str):
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{seller_id}/logistics/zipcode/{zip_code}/shipping/fee', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_seller_channel_type(self, external_seller_id: str, external_channel_id: str, channel_type: ChannelType):
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/type/{channel_type.value}', headers=self.headers)

	def __get_endpoint_base(self): 
		if self.environment == Environment.DEVELOPMENT and self.endpoint_development:
			return self.endpoint_development

		return self.environment.value