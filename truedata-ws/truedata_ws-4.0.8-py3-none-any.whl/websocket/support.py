from colorama import Style, Fore
from functools import wraps
from typing import Union
from copy import deepcopy
from datetime import datetime


class TouchlineData:
    def __init__(self):
        self.symbol = None
        self.symbol_id = None
        self.timestamp = None
        self.ltp = None
        self.ltq = None
        self.atp = None
        self.ttq = None
        self.open = None
        self.high = None
        self.low = None
        self.prev_close = None
        self.oi = None
        self.prev_oi = None
        self.turnover = None
        self.best_bid_price = None
        self.best_bid_qty = None
        self.best_ask_price = None
        self.best_ask_qty = None

    def __str__(self):
        return str(self.__dict__)


class TickLiveData:
    def __init__(self, symbol):
        # --Common Variables
        self.timestamp = None
        self.symbol_id = None
        self.symbol = symbol
        self.ltp = None
        self.ltq = None
        self.atp = None
        self.ttq = None
        self.day_open = None
        self.day_high = None
        self.day_low = None
        self.prev_day_close = None
        self.oi = None
        self.prev_day_oi = None
        self.turnover = None
        self.special_tag = ""
        self.tick_seq = None
        self.best_bid_price = None
        self.best_bid_qty = None
        self.best_ask_price = None
        self.best_ask_qty = None
        self.tick_type = None  # 0 -> touchline | 1 -> trade | 2 -> bidask
        # -- Calculated common
        self._change = None
        self._change_perc = None
        self._oi_change = None
        self._oi_change_perc = None
        self.populate_using_touchline = populate_touchline_data
        # -- Calculated specific
        # -- Unused
        # self.exchange = 'NSE'
        # - For level 2 and level 3 data
        # self.bids = []
        # self.asks = []

    def __eq__(self, other):
        res = True
        assert type(self) == type(other)
        try:
            if self.tick_seq != other.tick_seq\
                    or self.symbol != other.symbol\
                    or self.special_tag != other.special_tag:
                res = False
            elif self.best_bid_price != other.best_bid_price\
                    or self.best_bid_qty != other.best_bid_qty\
                    or self.best_ask_price != other.best_ask_price\
                    or self.best_ask_qty != other.best_ask_qty:
                res = False
        except AttributeError:
            pass
        return res

    def __str__(self):
        if self.special_tag == "":
            starting_formatter = ending_formatter = ""
        else:
            if self.special_tag == "H":
                starting_formatter = f"{Style.BRIGHT}{Fore.GREEN}"
                ending_formatter = f"{Style.RESET_ALL}"
            elif self.special_tag == "L":
                starting_formatter = f"{Style.BRIGHT}{Fore.RED}"
                ending_formatter = f"{Style.RESET_ALL}"
            elif self.special_tag == "O" or self.special_tag == "OHL":
                starting_formatter = f"{Style.BRIGHT}{Fore.BLUE}"
                ending_formatter = f"{Style.RESET_ALL}"
            else:
                starting_formatter = ending_formatter = ""
        op_dict = deepcopy(self.to_dict())
        return f"{starting_formatter}{str(op_dict)}{ending_formatter}"

    def to_dict(self):
        op_dict = deepcopy(self.__dict__)
        op_dict['change'] = self.change
        op_dict['change_perc'] = self.change_perc
        op_dict['oi_change'] = self.oi_change
        op_dict['oi_change_perc'] = self.oi_change_perc
        del op_dict['_change']
        del op_dict['_change_perc']
        del op_dict['_oi_change']
        del op_dict['_oi_change_perc']
        del op_dict['populate_using_touchline']
        return op_dict

    @property
    def change(self):
        try:
            self._change = self.ltp - self.prev_day_close
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with tick_type={self.tick_type} and tick_seq={self.tick_seq}")
        finally:
            return self._change

    @property
    def change_perc(self):
        try:
            self._change_perc = self.change * 100 / self.prev_day_close
        except ZeroDivisionError:
            self._change = self._change_perc = 0
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with tick_type={self.tick_type} and tick_seq={self.tick_seq}")
        finally:
            return self._change_perc

    @property
    def oi_change(self):
        try:
            self._oi_change = self.oi - self.prev_day_oi
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with tick_type={self.tick_type} and tick_seq={self.tick_seq}")
        finally:
            return self._oi_change

    @property
    def oi_change_perc(self):
        try:
            self._oi_change_perc = self._oi_change * 100 / self.prev_day_oi
        except ZeroDivisionError:
            self._oi_change = self._oi_change_perc = 0
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with tick_type={self.tick_type} and tick_seq={self.tick_seq}")
        finally:
            return self._oi_change_perc


class MinLiveData:
    def __init__(self, symbol):
        # --Common Variables
        self.timestamp = None
        self.symbol = symbol
        self.symbol_id = None
        self.day_high = None
        self.day_low = None
        self.day_open = None
        self.prev_day_close = None
        self.prev_day_oi = None
        self.oi = None
        self.ttq = None
        # --Obj specific
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None
        # -- Calculated common
        self._change = None
        self._change_perc = None
        self._oi_change = None
        self._oi_change_perc = None
        self.populate_using_touchline = populate_touchline_data
        # -- Calculated specific
        # --Unused
        # self.exchange = 'NSE'
        # -For level 2 and level 3 data
        # self.bids = []
        # self.asks = []

    def __eq__(self, other):
        res = True
        assert type(self) == type(other)
        if self.timestamp != other.timestamp\
                or self.symbol != other.symbol:
            res = False
        return res

    def __str__(self):
        return str(deepcopy(self.to_dict()))

    def to_dict(self):
        op_dict = deepcopy(self.__dict__)
        op_dict['change'] = self.change
        op_dict['change_perc'] = self.change_perc
        op_dict['oi_change'] = self.oi_change
        op_dict['oi_change_perc'] = self.oi_change_perc
        del op_dict['_change']
        del op_dict['_change_perc']
        del op_dict['_oi_change']
        del op_dict['_oi_change_perc']
        del op_dict['populate_using_touchline']
        return op_dict

    @property  # TODO: Use decorators for exceptions
    def change(self):
        try:
            self._change = self.close - self.prev_day_close
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with timestamp={self.timestamp}")
        finally:
            return self._change

    @property
    def change_perc(self):
        try:
            self._change_perc = self.change * 100 / self.prev_day_close
        except ZeroDivisionError:
            self._change = self._change_perc = 0
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with timestamp={self.timestamp}")
        finally:
            return self._change_perc

    @property
    def oi_change(self):
        try:
            self._oi_change = self.oi - self.prev_day_oi
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with timestamp={self.timestamp}")
        finally:
            return self._oi_change

    @property
    def oi_change_perc(self):
        try:
            self._oi_change_perc = self._oi_change * 100 / self.prev_day_oi
        except ZeroDivisionError:
            self._oi_change = self._oi_change_perc = 0
        except Exception as e:
            raise TDLiveCalcError(f"Encountered other change calculation error: {e} with symbol {self.symbol} with timestamp={self.timestamp}")
        finally:
            return self._oi_change_perc


def populate_touchline_data(data_obj: Union[TickLiveData, MinLiveData], touchline_obj: TouchlineData):
    # data_obj.timestamp = datetime.now()
    data_obj.symbol = touchline_obj.symbol
    data_obj.symbol_id = touchline_obj.symbol_id
    data_obj.day_high = touchline_obj.high
    data_obj.day_low = touchline_obj.low
    data_obj.day_open = touchline_obj.open
    data_obj.prev_day_close = touchline_obj.prev_close
    data_obj.prev_day_oi = touchline_obj.prev_oi
    data_obj.oi = touchline_obj.oi
    data_obj.ttq = touchline_obj.ttq
    if type(data_obj) is TickLiveData:
        data_obj.tick_type = 0
        data_obj.ltp = touchline_obj.ltp
    else:
        data_obj.close = touchline_obj.ltp


class TDLiveCalcError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Something's wrong with the live calculations- {self.args[0]}{Style.RESET_ALL}"


class TDHistoricDataError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Something's wrong with the historical data- {self.args[0]}{Style.RESET_ALL}"


class TDLiveDataError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Something's wrong with the live data- {self.args[0]}{Style.RESET_ALL}"


class TDInvalidRequestError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Invalid request ({self.args[0]}){Style.RESET_ALL}"


def historical_decorator(func):
    @wraps(func)
    def dec_helper(obj, contract, end_time, start_time, bar_size, options=None, bidask=False):
        if not options:
            options = {}
        if bar_size.lower() == 'tick' or bar_size.lower() == 'ticks':
            bar_size = 'tick'
            options['time_format'] = '%Y-%m-%dT%H:%M:%S'  # This is the response format
            options['processor_to_call'] = {'csv': obj.hist_csv_tick_data_to_dict_list, 'json': obj.hist_json_tick_data_to_dict_list}
        elif bar_size.lower() == 'eod':
            # start_time = start_time.split('T')[0]
            # end_time = end_time.split('T')[0]
            bar_size = 'eod'
            options['time_format'] = '%Y-%m-%d'  # This is the response format
            # options['time_format'] = '%Y-%m-%dT%H:%M:%S'  # This is the response format
            options['processor_to_call'] = {'csv': obj.hist_csv_bar_data_to_dict_list, 'json': obj.hist_json_bar_data_to_dict_list}
        else:
            bar_size = bar_size.replace(' ', '')
            if bar_size[-1] == 's':
                bar_size = bar_size[:-1]
            options['time_format'] = '%Y-%m-%dT%H:%M:%S'  # This is the response format
            options['processor_to_call'] = {'csv': obj.hist_csv_bar_data_to_dict_list, 'json': obj.hist_json_bar_data_to_dict_list}
        return func(obj, contract, end_time, start_time, bar_size, options, bidask)

    return dec_helper


def access_token_decorator(func):
    @wraps(func)
    def dec_helper(obj, *args, **kwargs):
        if obj.access_token_expiry_time < datetime.now():
            obj.hist_login()
        return func(obj, *args, **kwargs)
    return dec_helper