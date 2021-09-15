import json
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

import pandas as pd

from powerbot_backtesting.utils import _order_matching, _find_cache
from powerbot_backtesting.utils.constants import *


def generate_input_file(orderbooks):
	"""
	Generates a csv file to put positions and signals into to use with the BacktestingAlgo

	Args:
		orderbooks (dict{key: DataFrame}): Dictionary of order books

	Returns:
		csv file
	"""
	# File creation
	input_file = pd.DataFrame({"contract_id": [*orderbooks]})
	input_file["position"] = ""
	input_file.set_index("contract_id", inplace=True)

	# Caching
	cache_path = _find_cache().joinpath("analysis_input")
	cache_path.mkdir(parents=True, exist_ok=True)

	# File name
	f_count = 1
	while cache_path.joinpath(f"backtesting_input_{f_count}.csv").exists():
		f_count += 1
	input_file.to_csv(cache_path.joinpath(f"backtesting_input_{f_count}.csv"), sep=";")


class BacktestingAlgo(ABC):
	"""
	Class aiming to provide a backbone to backtesting strategies.

	This class is used by providing two parameters: the order books and an input file based on these order books.
	The input file can be generated with the command "generate_input_file". The output is a csv file that needs to be
	filled with positions and other signals you wish to utilize in your backtesting strategy.

	Any keyworded arguments you pass will be automatically added as class attributes. This allows you to only overwrite
	a single function and still be able to use all the parameters you need for your strategy.

	To write your own backtesting algorithm, create a new class that inherits from BacktestingAlgo and overwrite
	the algorithm function. All signals/ columns that you have added to the input file will be reflected as dictionary
	keys in self.params. Please be aware, that the column names will be the key names after conversion.

	The most important feature of this class is it's order matching logic. When writing your own algorithm, this
	function needs to be called whenever your calculations are done and you want to see if you would make any trades.

	Any trades you perform alter the order book and will also be gathered in a list of results.
	"""

	def __init__(self,
				 orderbooks: dict[str, pd.DataFrame],
				 file_input: Union[str, Path],
				 generate_report: bool = True,
				 **kwargs):
		self.orderbooks = orderbooks
		self.filename = file_input if isinstance(file_input, str) else str(file_input).split("\\")[-1]
		self.trade_list = {key: {} for key in [*self.orderbooks]}
		self.results = {key: {} for key in [*self.orderbooks]}
		self.generate_report = generate_report

		# Load file input
		cache_path = _find_cache().joinpath("analysis_input")

		try:
			self.algo_params = pd.read_csv(f"{cache_path}/{file_input}", sep=";")
		except FileNotFoundError:
			self.algo_params = pd.read_csv(file_input, sep=";")

		self.algo_params = self.algo_params.set_index("contract_id")

		# Convert all keyworded args to attributes
		[setattr(self, key, value) for key, value in kwargs.items()]

	def match_orders(self,
					 side: str,
					 orderbook: pd.DataFrame,
					 timestamp: str,
					 price: Union[int, float],
					 position: Union[int, float],
					 contract_time: int,
					 key: str,
					 order_execution: str) -> Decimal:
		"""
		Wrapper for _order_matching function.

		Matches orders according to input parameters; adds trades made to trade_list and returns the remaining quantity.

		The order_execution parameter can be added to decide according to which logic the quantity should be filled. Allowed
		values are:

		NON - No restriction, partial execution is allowed

		FOK - Fill or Kill, if order isn't filled completely by first matching order, next matching order is loaded ->
		if none match next order book is loaded

		IOC - Immediate and Cancel, order is executed to maximum extent by first matching order, next order book is loaded ->
		allows price adjustments

		Args:
			side (str): buy/sell
			orderbook (DataFrame): Single order book
			timestamp (str): Timestamp of order book
			price (int): Minimum/ Maximum Price for Transaction
			position (int, float): Quantity that can/ should be traded
			contract_time (int): contract time in minutes, either 60, 30 or 15
			key (str): Position in trade list
			order_execution (str): Type of order execution that should be simulated

		Returns:
			Decimal: remaining quantity
		"""
		return _order_matching(side, orderbook, timestamp, price, position, self.exec_orders_list, self.trade_list[key],
							   contract_time, order_execution)


	def generate_trading_report(self):
		"""
		Generates a report containing all trades made including prices, quantity and timestamps.

		Returns:
			bool
		"""
		cache_path = _find_cache().joinpath("analysis_output")
		cache_path.mkdir(parents=True, exist_ok=True)

		# File creation
		with open(cache_path.joinpath(self.filename.replace("input", "output").replace("csv", "json")), "w") as out:
			json.dump(self.results, out)

		return True

	def run(self) -> Union[dict, bool]:
		"""
		Main function to execute custom trading logic. Handles all necessary steps and then calls the custom algorithm
		function.

		Returns:
			dict or bool: generates json trading report or returns contents as dict
		"""

		for nr, (key, contract) in enumerate(self.orderbooks.items()):
			if isinstance(contract, pd.DataFrame) and contract.empty or not contract:
				self.results[key]["Remaining Quantity"] = "No data"
				continue

			self.exec_orders_list = {}

			self.params = self.algo_params.loc[key].to_dict()

			contract_time = key.split(" ")
			self.params["contract_time"] = int(
				(datetime.strptime(contract_time[3], TIME_HM) - datetime.strptime(contract_time[1],
																				  TIME_HM)).seconds / 60)
			# Overrideable function to set custom calculation logic on contract level
			self.adjust_params()

			# Iteration through every timestep/ orderbook
			for timestamp, orderbook in contract.items():
				# Overrideable function to set behaviour on order book level
				if not self.algorithm(timestamp, orderbook, key):
					break

			# If quantity remains
			if self.params["position"]:
				self.results[key]["Remaining Quantity"] = round(float(self.params["position"]), 1)

		# Create summary
		for contract, trades in self.trade_list.items():
			self.results[contract]["Initial Position"] = int(self.algo_params.loc[contract].position)
			self.results[contract]["Total Cash"] = round(sum([value["Cash"] for value in trades.values()]), 2)
			self.results[contract]["Trades"] = trades

		if self.generate_report:
			return self.generate_trading_report()

		return self.results

	def adjust_params(self):
		"""
		Overridable function that defines calculation logic on contract level. Any parameters that will be changed in
		this function will be usable for each iteration of the order books.

		This function should only be used to adjust the parameters in the member variable self.params. Please be aware,
		that deletion of the key "position" will lead to an error.
		"""
		return None

	@abstractmethod
	def algorithm(self,
				  timestamp: str,
				  orderbook: pd.DataFrame,
				  key: str) -> bool:
		"""
		Overridable function that defines behaviour and calculations for specific strategy. Please make sure to define
		the same input parameters as the original function.

		Since the order matching function already saves every important action it takes, it does not need any manual
		adjustments.

		The only requirement for this function is that at least the position has to be recalculated according to the
		return value of the order matching function. Every other parameter (e.g. price) can be changed according to the
		specific trading strategy.

		An example (position closer) has been defined here just to showcase how the function is supposed to work.
		Please be aware that all of the following logic will be overwritten by your own implementation.

		Args:
			timestamp (str): Timestamp of order book
			orderbook (pd.DataFrame): Order book
			key (str): Contract timeframe

		Returns:
			bool
		"""
		# Buy
		if self.params["position"] < 0:
			self.params["position"] = - self.match_orders(
				side="buy",
				orderbook=orderbook,
				timestamp=timestamp,
				price=self.params.get("price", 40) - 2,
				position=abs(self.params["position"]),
				contract_time=self.params["contract_time"],
				key=key,
				order_execution="NON")
			return True

		# Sell
		elif self.params["position"] > 0:
			self.params["position"] = self.match_orders(
				side="sell",
				orderbook=orderbook,
				timestamp=timestamp,
				price=self.params.get("price", 40) + 2,
				position=self.params["position"],
				contract_time=self.params["contract_time"],
				key=key,
				order_execution="NON")
			return True

		else:
			return False


def flexpos_algo(orderbooks: dict[str, pd.DataFrame],
                 marg_prices: list[float],
                 buy_sell_spread: list[float],
                 init_prod: list[float],
                 min_prod: list[float],
                 max_prod: list[float],
                 closing_from: int = 2,
                 marg_prices_pc: list[list[float]] = None) -> dict[str, dict]:
	"""
	Algorithm that connects a flexibility algorithm with a position closer. At the defined timestamp, the flexibility
	algo is replaced with the position closer algo, which tries to close a position with the provided information.

	Timestamps are not directly passed as arguments, but rather inferred by the closing_from parameter, which calculates
	the respective start times for the position closer based on the closing_from value and the delivery start of the
	contract.

	Args:
		orderbooks (dict{key: DataFrame}): Dictionary of Orderbooks
		marg_prices (list[float]): Marginal Price to fluctuate around/ close position
		buy_sell_spread (list[float]): Minimum Profit per MW
		init_prod (list[float]): Initial Quantity of produced MW
		min_prod (list[float]): Minimum Quantity of produced MW
		max_prod (list[float]): Maximum Quantity of produced MW
		closing_from (int): Amount of hours before contract delivery start algorithm should stop running at
		marg_prices_pc (list[list[float]]): Marginal prices specific for position closer (optional)

	Returns:
		dict[key: dict[Production_quant (float), Remaining_quant (float), Profit (float),
			Trades_Flex (list), Trades_PC (list)]]
	"""

	# Checking Parameters
	if not all(len(i) == len([*orderbooks]) for i in [marg_prices, buy_sell_spread, init_prod, min_prod, max_prod]):
		raise Exception(f"All parameters have to be same length as amount of contracts in orderbook!")

	# Executing Flex Algo
	results_flex = flex_algo(orderbooks, marg_prices, buy_sell_spread, init_prod, min_prod, max_prod, closing_from)

	# Setup for PC Algo
	positions = [v["Production"] for v in results_flex.values()]
	start_from = [datetime.strptime(i.replace(f"{str(i).split(' - ')[1]}", "").replace(" - ", ":00"), DATE_YMD_TIME_HMS)
	              for i in [*orderbooks]]
	orderbooks_pc = {key: {} for key in [*orderbooks]}

	for nr, (timestamp, contract) in enumerate(orderbooks.items()):
		for key, orderbook in contract.items():
			if datetime.strptime(key, DATE_YMD_TIME_HMS_TZ) >= start_from[nr].replace(tzinfo=timezone.utc):
				orderbooks_pc[timestamp][key] = orderbook
	marg_prices_pc = [[i, i] for i in marg_prices] if not marg_prices_pc else marg_prices_pc

	# Executing PC Algo
	results_pc = pc_algo(orderbooks_pc, positions, marg_prices_pc)

	# Summing up Results
	results_total = {
		key: {"Initial_quant": init_prod[nr], "Flex_quant": results_flex[key]["Production"], "Remaining_quant": 0,
		      "Profit": results_flex[key]["Profit"], "Trades_Flex": results_flex[key]["Trades"]} for nr, key in
		enumerate([*results_flex])}

	for key, contract in results_pc.items():
		for name, value in contract.items():
			if name == "Remaining_quant":
				results_total[key]["Remaining_quant"] = value
			if name == "Cash":
				results_total[key]["Profit"] = results_total[key]["Profit"] + Decimal(value)
			if name == "Trades":
				results_total[key]["Trades_PC"] = value

	return results_total


def flex_algo(orderbooks: dict[str, pd.DataFrame],
              marg_prices: list[float],
              buy_sell_spread: list[float],
              init_prod: list[float],
              min_prod: list[float],
              max_prod: list[float],
              closing_from: int = None) -> dict[str, dict]:
	"""
	Standard flexibility algorithm that aims to maximize profit by fluctuating around a marginal price.
	All parameters have to be given as lists of the same length as the amount of contracts in orderbooks.

	Args:
		orderbooks (dict{key: DataFrame}): Dictionary of Orderbooks
		marg_prices (list): Marginal Price to fluctuate around
		buy_sell_spread (list): Minimum Profit per KWh
		init_prod (list): Initial Quantity of produced MW
		min_prod (list): Minimum Quantity of produced MW
		max_prod (list): Maximum Quantity of produced MW
		closing_from (int): Amount of hours before contract delivery start algorithm should stop running at
			(only relevant for flexpos_algo)

	Returns:
		dict[key: dict[Production (float), Profit (float), Trades (list)]]
	"""
	# Setup
	trade_list = {key: {} for key in [*orderbooks]}
	results = {key: {} for key in [*orderbooks]}
	closing_timestamps = [
		datetime.strptime(i.replace(f"{str(i).split(' - ')[1]}", "").replace(" - ", ":00"), DATE_YMD_TIME_HMS) for i
		in [*orderbooks]] if closing_from else None

	for nr, (key, contract) in enumerate(orderbooks.items()):
		exec_orders_list = {}
		curr_prod = init_prod[nr]
		contract_time = key.split(" ")
		contract_time = int((datetime.strptime(contract_time[3], TIME_HM) - datetime.strptime(contract_time[1],
		                                                                                      TIME_HM)).seconds / 60)

		for timestamp, orderbook in contract.items():
			# Stopping Loop on closing Timestamp
			if closing_from and datetime.strptime(timestamp, DATE_YMD_TIME_HMS_TZ) >= closing_timestamps[nr].replace(tzinfo=timezone.utc):
				break
			# Buy
			if round(max_prod[nr] - curr_prod, 1) > 0.1:
				rem_quant_buy = _order_matching("buy", orderbook, timestamp, marg_prices[nr] - buy_sell_spread[nr],
				                                max_prod[nr] - curr_prod, exec_orders_list, trade_list[key],
				                                contract_time)

				curr_prod = max_prod[nr] - rem_quant_buy  # If Remaining Quantity. Subtract From Maximum

			# Sell
			if round(curr_prod - min_prod[nr], 1) > 0.1:
				rem_quant_sell = _order_matching("sell", orderbook, timestamp, marg_prices[nr] + buy_sell_spread[nr],
				                                 curr_prod - min_prod[nr], exec_orders_list, trade_list[key],
				                                 contract_time)

				curr_prod = min_prod[nr] + rem_quant_sell  # If Remaining Quantity, Add To Minimum

		cash = Decimal(sum([value["Cash"] for value in trade_list[key].values()]))  # Calculating Cash

		results[key]["Production"] = curr_prod
		results[key]["Profit"] = round(curr_prod * marg_prices[nr] - abs(cash), 2)
		results[key]["Trades"] = trade_list[key]

	return results


def pc_algo(orderbooks: dict[str, pd.DataFrame],
            positions: list[float],
            marg_prices: list[list[int]] = None) -> dict[str, dict]:
	"""
	Standard position closing algorithm that aims to close an open position, optionally taking a marginal price into
	consideration. Positional values have to match the amount of keys in the orderbooks in length (1 position per contract).

	Things to consider:
	This algorithm is best used with either a single orderbook for a certain timestamp that a position should be closed
	at or multiple orderbooks beginning from this timestamp. This simulates closing the position at the desired time.
	Alternatively, the flexpos_algo can be used to try to maximize profit before the position is closed.

	Args:
		orderbooks (dict{key: DataFrame}): Dictionary of Orderbooks
		positions (list): Positional values in MW (1 position per contract)
		marg_prices (list): List with 2 values representing the minimum amount an order can be matched with (bought or sold)

	Returns:
		dict[key: dict[Initial_quant (int/float), Remaining_quant (float), Cash (float), Trades (list)]]
	"""
	# Orderbooks dict object consists of keys for each contract with the aggregated orderbooks as dataframes attached

	# Checking Values
	if not isinstance(positions, list) or len(positions) != len([*orderbooks]):
		raise Exception("Parameter positions has to be list of floats of same length as contracts in orderbook!")

	if marg_prices:
		if not isinstance(marg_prices, list) or not all(len(i) == 2 for i in marg_prices):
			raise Exception("Marginal prices have to be provided as a list, containing 2 floats/integers representing"
			                " buy price and sell price!")
	else:
		marg_prices = [[1000, 0] for _ in [*orderbooks]]

	# Setup
	exec_orders_list = {}
	trade_list = {key: {} for key in [*orderbooks]}
	results = {key: {"Initial_quant": positions[nr], "Remaining_quant": 0, "Cash": 0, "Trades": []} for nr, key in
	           enumerate([*orderbooks])}

	for nr, (key, contract) in enumerate(orderbooks.items()):
		pos = positions[nr]
		buy_price = marg_prices[nr][0]
		sell_price = marg_prices[nr][1]
		contract_time = key.split(" ")
		contract_time = int((datetime.strptime(contract_time[3], TIME_HM) - datetime.strptime(contract_time[1],
		                                                                                      TIME_HM)).seconds / 60)

		if isinstance(contract, pd.DataFrame) and contract.empty or not contract:
			results[key]["Remaining_quant"] = "No data"
			continue

		for timestamp, orderbook in contract.items():
			# Buy
			if pos < 0:
				pos = -(_order_matching("buy", orderbook, timestamp, buy_price, abs(pos), exec_orders_list,
				                        trade_list[key], contract_time))

			# Sell
			elif pos > 0:
				pos = _order_matching("sell", orderbook, timestamp, sell_price, pos, exec_orders_list, trade_list[key],
				                      contract_time)

			else:
				break
		if pos:
			results[key]["Remaining_quant"] = round(pos, 1)

	for contract, trades in trade_list.items():
		results[contract]["Cash"] = round(sum([value["Cash"] for value in trades.values()]), 2)
		results[contract]["Trades"] = trades

	return results

