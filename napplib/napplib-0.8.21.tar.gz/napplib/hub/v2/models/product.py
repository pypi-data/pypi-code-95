# build-in imports
from dataclasses 	import dataclass
from typing 		import List
from typing 		import Optional


@dataclass
class HubProductAttribute:
	name	: str
	value	: str


@dataclass
class HubProduct:
	category_name			: str
	brand_name				: str
	product_code			: str
	product_external_code	: str
	product_napp_code		: str
	product_name			: str
	product_is_enabled		: bool
	sku						: str
	ean						: str
	name					: str
	description				: str
	weight_net				: float
	weight_m3				: float
	height					: float
	width					: float
	length					: float
	packing_height			: float
	packing_width			: float
	packing_length			: float
	external_id				: str
	external_category		: str
	napp_sku_id				: int
	cross_docking			: int
	is_enabled				: bool
	list_price				: float
	price					: float
	stock_quantity			: int
	attributes				: List[HubProductAttribute]
	images					: List[str]
