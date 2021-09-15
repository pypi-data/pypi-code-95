import os
import pickle
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
from time import sleep
from typing import Union
import json

import pandas as pd
from powerbot_client import ApiClient, TradesApi, SignalsApi, Signal, Trade, InternalTrade, OrdersApi, OwnOrder

from powerbot_backtesting.utils.constants import *
from powerbot_backtesting.models import HistoryApiClient


def _get_private_data(api_client: ApiClient,
					  data_type: str,
					  time_from: datetime = None,
					  time_till: datetime = None,
					  delivery_area: str = None,
					  portfolio_id: list[str] = None,
					  active_only: bool = False) -> list[Union[InternalTrade, OwnOrder, Trade, Signal]]:
	"""
	Underlying function of all private data requests to PowerBot. Loads the specified collection according to the
	parameters given.

	Args:
		api_client: PowerBot ApiClient
		data_type (str): Either internal_trade, own_trade, own_order or signal
		time_from (str/ datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
		time_till (str/ datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
		delivery_area (str): EIC Area Code for Delivery Area
		portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.
		active_only (bool):  True if only active orders should be loaded. If False, loads also hibernate and inactive.

	Returns:
		list[Union[InternalTrade, OwnOrder, Trade, Signal]]
	"""
	param_mapping = {
		"internal_trade": {"delivery_within_start": time_from, "delivery_within_end": time_till, "limit": 100},
		"own_trade": {"delivery_within_start": time_from, "delivery_within_end": time_till, "limit": 500},
		"own_order": {"active_only": active_only, "limit": 500},
		"signal": {"received_from": time_from, "received_to": time_till, "limit": 500}
	}
	func_mapping = {
		"internal_trade": TradesApi(api_client).get_internal_trades,
		"own_trade": TradesApi(api_client).get_trades,
		"own_order": OrdersApi(api_client).get_own_orders,
		"signal": SignalsApi(api_client).get_signals
	}

	coll = []
	more_obj = True
	offset = 0
	params = {**param_mapping[data_type]}

	if portfolio_id:
		params["portfolio_id"] = portfolio_id
	if delivery_area:
		params["delivery_area"] = delivery_area

	while more_obj:
		new_objs = func_mapping[data_type](offset=offset, **params)
		if len(new_objs):
			coll += new_objs
			offset += len(new_objs)
		else:
			more_obj = False
		sleep(0.2)

	return coll


def _cache_data(data_type: str,
				data: dict[str, pd.DataFrame],
				delivery_area: str,
				exchange: str = None,
				api_client: Union[ApiClient, HistoryApiClient] = None,
				timesteps: int = 0,
				time_unit: str = None,
				gzip_files: bool = True,
				as_json: bool = True,
				as_csv: bool = False,
				as_pickle: bool = False):
	"""
	Function to be called by data request functions to cache loaded data in a reusable format. Automatically generates
	a folder to cache loaded files, if it cannot find an existing one.

	Args:
		data_type (str): One of the following: trades, ordhist, ohlc, orderbook
		data (dict): Dictionary of DataFrames
		delivery_area (str): EIC Area Code for Delivery Area
		exchange (str): Exchange e.g. epex, nordpool, southpool, etc.
		api_client: PowerBot ApiClient
		timesteps (int): only necessary if data_type is ohlc or orderbooks
		time_unit (str): only necessary if data_type is ohlc or orderbooks
		gzip_files (bool): True if cached files should be gzipped
		as_json (bool): True per default, except for orderbooks (optional feature)
		as_csv (bool): if True, will save files as CSV, additionally to JSON
		as_pickle (bool): False per default, except for orderbooks
	"""
	# Setup
	host = api_client.configuration.host if isinstance(api_client, ApiClient) else None
	environment = "staging" if host and host.split("/")[2].split(".")[0] == "staging" else "prod"
	exchange = host.split("/")[4] if host else api_client.exchange if isinstance(api_client, HistoryApiClient) else exchange
	folder = "raw" if data_type in ["trades", "ordhist", "contracts"] else "processed"
	compression = "gzip" if gzip_files else "infer"
	file_ending = ".gz" if gzip_files else ""

	# Caching
	for key, value in data.items():
		delivery_date = datetime.strptime(key.split(" ")[0], "%Y-%m-%d")
		year_month = delivery_date.strftime("%Y-%m")
		day_month = delivery_date.strftime("%m-%d")
		file_name = key.replace(f"{str(key).split(' ')[0]}", "").replace(":", "-")
		file_name = f"{file_name}_{data_type}" if folder == "raw" else f"{file_name}_{data_type}_{timesteps}{time_unit}"
		file_name = f"{delivery_date.date()}{file_name}" if file_name.startswith("_") else file_name

		# Check if __cache__ already exists
		cache_path = _find_cache().joinpath(
			f"{environment}\\{exchange}_{delivery_area}\\{year_month}\\{day_month}\\{folder}")

		# Assure That Directory Exists
		cache_path.mkdir(parents=True, exist_ok=True)

		# Cache File If It Doesn't Exist Yet
		if as_json and not cache_path.joinpath(f"{file_name}.json{file_ending}").exists():
			value.to_json(cache_path.joinpath(f"{file_name}.json{file_ending}"), date_format="iso", date_unit="us",
			              compression=compression)

		if as_csv and not cache_path.joinpath(f"{file_name}.csv").exists():
			value.to_csv(cache_path.joinpath(f"{file_name}.csv{file_ending}"), sep=";", compression=compression)

		if as_pickle and not cache_path.joinpath(f"{file_name}.p").exists():
			pickle.dump(value, open(cache_path.joinpath(f"{file_name}.p"), "wb"))


def _find_cache() -> Path:
	"""
	Functions returns location of __cache__ directory if it can be found within 3 parent directories based on the
	location of the file backtesting functions are called from.

	If multiple projects lie within a directory that can be reached within 3 parent directories from where this
	function is called, it might find a cache directory that does not lie directly in the current projects root
	directory. This can be confusing, however, it does not restrict functionality.

	This fact can also be used on purpose by manually creating a __pb_cache__ directory one parent above, that can be
	shared by multiple projects that require historic data.

	Proposed structure:
	parent_dir
	| __pb_cache__
	|
	|--- project_1
	|	|   file.py
	|
	|--- project_2
	|	|   file.py
	|
	|--- project_3
		|   file.py

	Returns:
		Path
	"""
	if Path("__pb_cache__").exists():
		return Path("__pb_cache__")

	cache_path = None
	root_path = Path().cwd()

	for _ in range(3):
		cache_path = [root for root, directory, file in os.walk(root_path) if "__pb_cache__" in root]

		# Check if cache was found
		if cache_path:
			cache_path = Path(cache_path[0])
			break

		root_path = root_path.parent

	if not cache_path:
		cache_path = Path().cwd().joinpath("__pb_cache__")

	return cache_path


def _get_file_cachepath(api_client: Union[ApiClient, HistoryApiClient], contract_key: str, delivery_area: str) -> str:
	"""
	Helper function that constructs most of the path of a cached file.

	Args:
		api_client: PowerBot ApiClient if loading from API else HistoryApiClient
		contract_key (str): Key of dictionary
		delivery_area (str): EIC Area Code for Delivery Area

	Returns:
		filepath: str
	"""
	environment = api_client.configuration.host.split("/")[2].split(".")[0] if isinstance(api_client, ApiClient) else None
	environment = "staging" if environment == "staging" else "prod"
	market = api_client.configuration.host.split("/")[4] if isinstance(api_client, ApiClient) else api_client.exchange
	delivery_date = datetime.strptime(contract_key.split(" ")[0], DATE_YMD)
	year_month = delivery_date.strftime(DATE_YM)
	day_month = delivery_date.strftime(DATE_MD)
	file_name = contract_key.replace(f"{str(contract_key).split(' ')[0]}", "").replace(":", "-")

	return f"{environment}\\{market}_{delivery_area}\\{year_month}\\{day_month}\\raw\\{file_name}"


def _check_contracts(contract, delivery_areas: list[str], products: list[str], allow_udc: bool) -> bool:
	"""
	Helper function to determine if contract is of interest and should be added to contract dictionary.

	Args:
		contract: Contract Object
		delivery_areas: List of EIC-codes
		products: List of products

	Returns:
		bool
	"""
	if contract.exchange in SYSTEMS["M7"]:
		if delivery_areas and contract.delivery_areas and not any(
				area in contract.delivery_areas for area in delivery_areas) \
				or delivery_areas and contract.contract_details["deliveryAreas"] and not any(
			area in contract.contract_details["deliveryAreas"] for area in delivery_areas) \
				or delivery_areas and not contract.delivery_areas and not contract.contract_details["deliveryAreas"] \
				or products and contract.product not in products \
				or not products and "10YGB----------A" not in delivery_areas and contract.product == "GB_Hour_Power"\
				or contract.type == "UDC" and not allow_udc:
			return False

	else:
		if delivery_areas and contract.delivery_areas and not any(
				area in contract.delivery_areas for area in delivery_areas) \
				or delivery_areas and not contract.delivery_areas \
				or products and contract.product not in products \
				or contract.type == "UDC" and not allow_udc:
			return False

	return True


def _order_matching(order_side: str,
                    orderbook: pd.DataFrame,
                    timestamp: str,
                    price: Union[int, float],
                    quantity: Union[int, float, Decimal],
                    exec_orders_list: dict[str, int],
                    trade_list: dict[int, dict[str, int]],
                    contract_time: int,
                    order_execution: str = "NON") -> Decimal:
	"""
	Matches orders according to input parameters; adds trades made to trade_list and returns the remaining quantity.

	The order_execution parameter can be added to decide according to which logic the quantity should be filled. Allowed
	values are:

	NON - No restriction, partial execution is allowed

	FOK - Fill or Kill, if order isn't filled completely by first matching order, next matching order is loaded ->
	if none match next order book is loaded

	IOC - Immediate and Cancel, order is executed to maximum extent by first matching order, next order book is loaded ->
	allows price adjustments

	Args:
		order_side (str): buy/sell
		orderbook (DataFrame): Single order book
		timestamp (str): Timestamp of order book
		price (int): Minimum/ Maximum Price for Transaction
		quantity (int): Quantity to buy/sell
		exec_orders_list (dict): Dictionary of already matched order IDs
		trade_list (list): List of executed trades
		contract_time (int): contract time in minutes, either 60, 30 or 15
		order_execution (str): Type of order execution that should be simulated

	Returns:
		Decimal: remaining quantity
	"""

	# Transform Values to Decimals
	getcontext().prec = 8
	price = round(Decimal(price), 2)
	quantity = round(Decimal(quantity), 1)
	cash_adjust = {60: 1, 30: 2, 15: 4}

	order_type = {"buy": "ask", "sell": "bid"}
	operator = {"buy": -1, "sell": 1}

	orderbook = orderbook.loc[orderbook.type == order_type[order_side]]

	if order_type[order_side] == "ask":
		orderbook = orderbook.sort_values(by=['price', 'as_of'], ascending=[True, False])
	else:
		orderbook = orderbook.sort_values(by=['price', 'as_of'], ascending=[False, False])

	for ind, row in orderbook.iterrows():
		if quantity > 0:
			open_qty = round(Decimal(row["quantity"]), 1)

			if row["order_id"] in [*exec_orders_list]:  # Check If Already Matched
				if round(Decimal(exec_orders_list[row["order_id"]]), 1) == open_qty:
					continue  # Skip If Quantity Depleted
				open_qty = open_qty - Decimal(exec_orders_list[row["order_id"]])  # If Matched, Adjust Open Quantity

			# Check If Price Is Matched
			price_match = Decimal(row["price"]) <= price if order_side == "buy" else Decimal(row["price"]) >= price

			if price_match:
				# If order can't be filled completely
				if order_execution == "FOK" and quantity > open_qty:
					continue

				traded_quant = round(min(open_qty, quantity), 1)
				# Calculate Cost
				cash = traded_quant * Decimal(row.price) * operator[order_side] / cash_adjust[contract_time]

				trade_list[len([*trade_list]) + 1] = {"Side": order_side,
													  "Quantity": float(str(traded_quant)),
													  "Price": row["price"],
													  "Cash": float(str(cash)),
													  "Timestamp": timestamp}

				if row["order_id"] in [*exec_orders_list]:
					# If Existing, Adjust Quantity
					if order_side == "buy":
						exec_orders_list[row["order_id"]] += round(min(open_qty, quantity), 1)
					else:
						exec_orders_list[row["order_id"]] -= round(min(open_qty, quantity), 1)
				else:
					exec_orders_list[row["order_id"]] = round(min(open_qty, quantity), 1)

				quantity -= round(traded_quant, 1)  # Adjust Quantity

				# Break if quantity has been executed
				if order_execution == "IOC":
					break

			else:
				break
		else:
			break

	return quantity


def _orderbook_data_transformation(orders: pd.DataFrame) -> pd.DataFrame:
	"""
	Function transforms data in passed dataframe to be compatible with process_orderbooks function

	Args:
		orders (pd.DataFrame): DataFrame containing order data

	Returns:
		pd.Dataframe
	"""
	if not isinstance(orders, pd.DataFrame):
		return pd.DataFrame()

	bids_asks = []
	# Processing
	if "orders" in orders.columns:
		orders_all = orders["orders"].to_list()
		dates_all = [str(i) for i in orders["as_of"].to_list()]
		deltas = orders.delta.to_list() if "delta" in orders.columns else [1 for _ in range(len(dates_all))]
		for nr, val in enumerate(orders_all):
			for k, v in val.items():
				if v and k in ["ask", "bid"]:
					for x in v:
						x["as_of"] = dates_all[nr]
						x["type"] = "bid" if k == "bid" else "ask"
						x["delta"] = val.get("delta", deltas[nr])
						bids_asks.append(x)

	else:
		for nr, row in orders.iterrows():
			for side in ["bids", "asks"]:
				if row[side] and not isinstance(row[side], float):
					for entry in row[side]:
						entry["type"] = side[:-1]
						entry["as_of"] = row["as_of"].tz_convert(timezone.utc) if row["as_of"].tzinfo else row["as_of"].tz_localize(timezone.utc)
						entry["delta"] = row["delta"]
						bids_asks.append(entry)

	df_bid_asks = pd.DataFrame(bids_asks)
	df_bid_asks = df_bid_asks.drop(columns=["exe_restriction", "delivery_area", "order_entry_time"],
								   errors="ignore")
	return df_bid_asks


def _delta_filter(orderbook: pd.DataFrame) -> pd.DataFrame:
	"""
	Function filters dataframe by orders that are not delta reports. If delta is False, all orders before this order
	have to be deleted.

	Since delta: false is assigned to a revision of a contract, it can contain more than just one order. Therefore, all
	orders in a delta: false revision have that flag assigned. This function takes this situation in account, loading
	the last delta: false and going back until the space between two orders that have delta: false is bigger than 1.

	Args:
		orderbook (pd.Dataframe): Preliminary order book

	Returns:
		pd.Dataframe
	"""
	ind = orderbook[(~orderbook.delta) | (orderbook.delta == 0)].index
	if not ind.empty:
		last_delta = ind[-1]

		for i in ind[::-1]:
			if i == (last_delta - 1) or i == last_delta:
				last_delta = i
			else:
				break

		return orderbook.loc[orderbook.index >= last_delta].drop(columns=["delta"])

	return orderbook.drop(columns=["delta"])


def _historic_contract_transformation(path_to_file: str, exchange: str) -> pd.DataFrame:
	if exchange in SYSTEMS["M7"]:
		index = pd.json_normalize(json.load(open(path_to_file)))[
			["deliveryAreas", "deliveryEnd", "deliveryStart", "details.contractId", "details.prod", "details.actPoint",
			 "details.expPoint", "details.undrlngContracts.contractId"]]
	else:
		index = pd.DataFrame(json.load(open(path_to_file)))
		index.rename(columns={"_id": "contract_id", "product": "_product"}, inplace=True)

	index.rename(columns={"details.contractId": 'contract_id', "deliveryAreas": 'delivery_areas',
	                      "deliveryStart": 'delivery_start', "deliveryEnd": 'delivery_end',
	                      "details.prod": '_product', "details.actPoint": 'activation_time',
	                      "details.expPoint": 'expiry_time', 'details.undrlngContracts.contractId': 'undrlng_contracts'},
	             inplace=True)

	return index


def _historic_data_transformation(files: list, exchange: str, filetype: str) -> pd.DataFrame:
	"""
	Function transforms historic data into correct format to be used with other data processing functions.

	Args:
		files (list): List of files to be transformed
		exchange (str): Exchange e.g. epex, nordpool, southpool, etc.
		filetype (str): either trades or orders

	Returns:
		pd.DataFrame
	"""
	# Append contracts that are in the same timeframe to one DataFrame
	df = None
	for file in files:
		if not isinstance(df, pd.DataFrame):
			df = pd.read_json(file)
		else:
			df = df.append(pd.read_json(file), ignore_index=True)

	if exchange in SYSTEMS["M7"]:
		if filetype == "trades":
			df.drop(columns=["revisionNo"], inplace=True)
			df.rename(columns={"_id": "trade_id", "contractId": 'contract_id', "tradeExecTime": 'exec_time',
							   "apiTimeStamp": 'api_timestamp', "buyDeliveryArea": 'buy_delivery_area',
							   "sellDeliveryArea": 'sell_delivery_area', "selfTrade": 'self_trade',
							   "qty": 'quantity', "px": 'price', "pxqty": 'prc_x_qty'},
					  inplace=True)

			df.quantity = df.quantity / 100
			df.price = df.price / 100
			df.prc_x_qty = df.prc_x_qty / 10000

		if filetype == "orders":
			df.rename(columns={"asOf": "as_of", "bestAskPrice": "best_ask", "bestAskQuantity": "best_ask_qty",
							   "bestBidPrice": "best_bid", "bestBidQuantity": "best_bid_qty",
							   "contractId": "contract_id", "deliveryArea": "delivery_area", "full": "delta",
							   "lastPrice": "last_price", "lastQuantity": "last_qty",
							   "lastUpdate": "last_trade_time", "revisionNo": "revision_no"},
					  inplace=True)

			# Getting information from details field if missing on upper level
			meta_cols = {"best_bid": "bestBidPx", "best_ask": "bestAskPx", "best_bid_qty": "bestBidQty",
						 "last_price": "lastPx", "last_qty": "lastQty", "last_trade_time": "lastTradeTime",
						 "volume": "totalQty", "high": "highPx", "low": "lowPx", "revision_no": "revisionNo"}
			missing_details = {k: v for k, v in meta_cols.items() if k not in df.columns}
			details = df.details.tolist()

			for k, v in missing_details.items():
				if v in ["lastPx", "lastQty", "highPx", "lowPx", "totalQty"]:
					df[k] = [i[v] / 100 if v in [*i] else None for i in details]
				else:
					df[k] = [i[v] if v in [*i] else None for i in details]

			contract_id = df.contract_id.unique().tolist()[0]
			delivery_area = df.delivery_area.unique().tolist()[0]
			asks = [i["sellOrdrList"]["ordrBookEntry"] if i["sellOrdrList"] else None for i in df.details.tolist()]
			bids = [i["buyOrdrList"]["ordrBookEntry"] if i["buyOrdrList"] else None for i in df.details.tolist()]

			conversion = lambda i: [{"order_id": v["ordrId"], "price": v["px"] / 100, "quantity": v["qty"] / 100,
									 "contract_id": contract_id, "delivery_area": delivery_area,
									 "order_entry_time": v["ordrEntryTime"]} for v in i]

			asks = [conversion(i) if i else None for i in asks]
			bids = [conversion(i) if i else None for i in bids]

			df["asks"] = asks
			df["bids"] = bids

			df.drop(columns=["_id", "details", "avwa", "bvwa"], inplace=True, errors="ignore")

	else:
		if filetype == "trades":
			# Filter out deleted Trades
			df = df.loc[~df.deleted]

			df.rename(columns={"_id": "trade_id", "tradeTime": 'exec_time', "apiTimestamp": "api_timestamp",
							   "companyTrade": "self_trade"},
					  inplace=True)

			details = df.legs.tolist()

			df["contract_id"] = [i[0]["contractId"] for i in details]
			df["buy_delivery_area"] = [NORDPOOL_EIC_CODES[i[0]["deliveryAreaId"]] if i else None for i in
									   details]
			df["sell_delivery_area"] = [NORDPOOL_EIC_CODES[i[1]["deliveryAreaId"]] if len(i) == 2 else None for
										i in
										details]
			df["quantity"] = [float(i[0]["quantity"]) for i in details]
			df["price"] = [float(i[0]["unitPrice"]) for i in details]
			df["prc_x_qty"] = round(df.price * df.quantity, 2)

			df.drop(columns=["eventSequenceNo", "legs", "mediumDisplayName", "deleted", "state"], inplace=True)

		if filetype == "orders":
			df.rename(
				columns={"apiTimestamp": "as_of", "bestAskPrice": "best_ask", "bestAskQuantity": "best_ask_qty",
						 "bestBidPrice": "best_bid", "bestBidQuantity": "best_bid_qty", "bidsAndAsks": "details",
						 "contractId": "contract_id", "deliveryArea": "delivery_area", "full": "delta",
						 "lastPrice": "last_price", "lastQuantity": "last_qty", "lowestPrice": "low",
						 "highestPrice": "high", "lastTradeTime": "last_trade_time", "revision": "revision_no",
						 "turnover": "total_quantity"},
				inplace=True)

			df["delta"] = [False if "snapshot" in i else True for i in df.details]
			df.revision_no = [i for i in range(0, len(df))]
			df.delivery_area = [NORDPOOL_EIC_CODES[i] for i in df.delivery_area.tolist()]
			asks = [i["asks"] if "asks" in i else None for i in df.details.tolist()]
			bids = [i["bids"] if "bids" in i else None for i in df.details.tolist()]

			conversion = lambda i: [
				{"order_id": v["orderId"], "price": v["price"], "quantity": v["quantity"],
				 "contract_id": v["contractId"], "delivery_area": NORDPOOL_EIC_CODES[v["deliveryArea"]],
				 "order_entry_time": v["createdAt"]} for v in i]

			df["asks"] = [conversion(i) if i else None for i in asks]
			df["bids"] = [conversion(i) if i else None for i in bids]

			df.drop(columns=["_id", "details", "updatedAt"], inplace=True)

	return df