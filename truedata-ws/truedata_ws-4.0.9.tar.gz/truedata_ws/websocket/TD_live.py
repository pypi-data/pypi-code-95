from websocket import WebSocketApp
from threading import Thread
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import json
from copy import deepcopy
from collections import defaultdict

from colorama import Style, Fore


class LiveClient(WebSocketApp):

    def __init__(self, parent_app, url, *args):
        WebSocketApp.__init__(self, url, on_open=self.ws_open, on_error=self.ws_error, on_message=self.on_msg_func, on_close=self.ws_close, *args)
        self.segments = []
        self.max_symbols = 0
        self.remaining_symbols = 0
        self.valid_until = ''
        self.contract_mapping = {}
        self.subscription_type = ''
        self.confirm_heartbeats = 1
        self.store_last_n_heartbeats = self.confirm_heartbeats + 7
        self.heartbeat_interval = 5
        self.heartbeat_buffer = 0.5
        time_of_creation = datetime.now()
        self.last_n_heartbeat = [time_of_creation - relativedelta(seconds=i * self.heartbeat_interval) for i in range(-self.store_last_n_heartbeats, 0)]
        self.parent_app = parent_app
        self.logger = self.parent_app.logger
        self.disconnect_flag = False
        self.heartbeat_check_thread = Thread(target=self.check_heartbeat, daemon=True)
        self.trade_callback = None
        self.bar_callback = None
        self.bidask_callback = None
        # if self.parent_app.live_port == 8086 or self.parent_app.live_port == 8084:
        #     # self.heartbeat_check_thread.start()
        #     pass

    def check_connection(self):
        base_heartbeat = self.last_n_heartbeat[-self.confirm_heartbeats]
        check_time = datetime.now()
        time_diff = check_time - base_heartbeat
        is_connected = time_diff.total_seconds() > ((self.heartbeat_interval + self.heartbeat_buffer) * self.confirm_heartbeats)  # 3 > 5 + 0.5
        return is_connected

    def check_heartbeat(self):
        while True:
            time.sleep(self.heartbeat_interval)
            if self.disconnect_flag:
                self.logger.info(f"{Fore.WHITE}Removing hand from the pulse...{Style.RESET_ALL}")
                break
            if self.check_connection():
                self.logger.debug(f"{Style.BRIGHT}{Fore.RED}Failed Heartbeat @ {datetime.now()} because of last at {self.last_n_heartbeat[-self.confirm_heartbeats]}{Style.RESET_ALL}")
                self.logger.info(f"{Style.BRIGHT}{Fore.RED}Attempting reconnect @ {Fore.CYAN}{datetime.now()}{Style.RESET_ALL}")
                restart_successful = self.reconnect()
                if restart_successful:
                    self.logger.info(f"{Style.BRIGHT}{Fore.GREEN}Successful restart @ {Fore.CYAN}{datetime.now()}{Style.RESET_ALL}")
                    time.sleep((self.heartbeat_interval + self.heartbeat_buffer))
                    recover_start, recover_end = self.get_largest_diff(self.last_n_heartbeat)
                    # self.logger.debug(f"\t\t\t{len(self.last_n_heartbeat)} - {self.last_n_heartbeat}")
                    self.recover_from_time_missed(recover_start, recover_end)
                else:
                    self.logger.info(f"{Style.BRIGHT}{Fore.RED}Failed restart @ {Fore.CYAN}{datetime.now()}{Style.RESET_ALL}")

    @staticmethod
    def get_largest_diff(time_series):
        big_li = deepcopy(time_series.pop(0))
        small_li = deepcopy(time_series.pop())
        diffs = [i[0]-i[1] for i in zip(big_li, small_li)]
        start_gap_index = max(range(len(diffs)), key=lambda i: diffs[i])
        return time_series[start_gap_index], time_series[start_gap_index+1]

    def recover_from_time_missed(self, start_time, end_time):
        self.logger.info(f"{Style.BRIGHT}{Fore.YELLOW}Initiating recovery from {Fore.GREEN}{start_time}{Fore.YELLOW} till {Fore.GREEN}{end_time}{Fore.YELLOW} "
                         f"which are last green heartbeats from server...{Style.RESET_ALL}")

    def reconnect(self):
        self.close()
        t = Thread(target=self.run_forever, daemon=True)
        t.start()
        time.sleep(1)
        is_td_connected = False
        while not is_td_connected:
            time.sleep(self.heartbeat_interval + self.heartbeat_buffer)
            is_td_connected = self.check_connection()
        return is_td_connected

    def on_msg_func(self, *args):
        message = args[-1]
        msg = json.loads(message)
        if 'message' in msg.keys():
            self.handle_message_data(msg)
        if 'trade' in msg.keys():
            trade = msg['trade']
            self.handle_trade_data(trade)
        elif 'bidask' in msg.keys():
            bidask = msg['bidask']
            self.handle_bid_ask_data(bidask)
        elif any(['min' in key for key in msg.keys()]):
            bar_key = next(key for key in msg.keys() if 'min' in key)
            bar_data = msg[bar_key]
            self.handle_bar_data(bar_data)

    def handle_message_data(self, msg):
        if msg['success']:
            if msg['message'] == 'HeartBeat':
                self.handle_heartbeat(msg['timestamp'])
            elif msg['message'] == 'TrueData Real Time Data Service':  # Connection success message
                # self.logger.info(f"{Style.BRIGHT}{Fore.WHITE}You have subscribed for {msg['maxsymbols']} "
                #                  f"symbols across {msg['segments']} until {msg['validity']} with type of stream "
                #                  f"as {msg['subscription']}...{Style.RESET_ALL}")
                self.logger.warning(f"{Style.NORMAL}{Fore.BLUE}Connected successfully to {msg['message']}... {Style.RESET_ALL}")
                self.subscription_type = msg['subscription']
            elif msg['message'] in ['symbols added', 'touchline']:
                self.add_contract_details(msg['symbollist'])
            elif msg['message'] == 'symbols removed':
                self.remove_symbols(msg['symbollist'])
        else:
            self.logger.error(f"{Style.BRIGHT}{Fore.RED}The request encountered an error - {msg['message']}{Style.RESET_ALL}")

    def handle_heartbeat(self, server_timestamp):
        self.logger.debug(f'Server heartbeat received at {server_timestamp}')
        timestamp = datetime.strptime(server_timestamp, "%Y-%m-%dT%H:%M:%S.%f")  # old format + ((26 - len(server_timestamp)) * "0")
        self.last_n_heartbeat = self.last_n_heartbeat[1:]
        self.last_n_heartbeat.append(timestamp)

    def remove_symbols(self, contracts):
        for contract_info in contracts:
            contract = contract_info.split(':')[0]
            for req_id in self.parent_app.symbol_mkt_id_map[contract.upper()]:
                del self.parent_app.live_data[req_id]
                del self.parent_app.touchline_data[req_id]
                if '+' in self.subscription_type:
                    del self.parent_app.min_live_data[req_id]
            del self.parent_app.symbol_mkt_id_map[contract.upper()]

    def add_contract_details(self, contracts_list):
        for contract_details in contracts_list:
            if contract_details is not None:
                self.contract_mapping[int(contract_details[1])] = symbol = contract_details[0]
                for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                    self.parent_app.touchline_data[ticker_id].symbol_id = int(contract_details[1])
                    self.parent_app.touchline_data[ticker_id].timestamp = datetime.strptime(contract_details[2], '%Y-%m-%dT%H:%M:%S')
                    self.parent_app.touchline_data[ticker_id].symbol = symbol
                    self.parent_app.touchline_data[ticker_id].ltp = float(contract_details[3])
                    self.parent_app.touchline_data[ticker_id].ltq = float(contract_details[4])
                    self.parent_app.touchline_data[ticker_id].atp = float(contract_details[5])
                    self.parent_app.touchline_data[ticker_id].ttq = int(contract_details[6])
                    self.parent_app.touchline_data[ticker_id].open = float(contract_details[7])
                    self.parent_app.touchline_data[ticker_id].high = float(contract_details[8])
                    self.parent_app.touchline_data[ticker_id].low = float(contract_details[9])
                    self.parent_app.touchline_data[ticker_id].prev_close = float(contract_details[10])
                    self.parent_app.touchline_data[ticker_id].oi = int(contract_details[11])
                    self.parent_app.touchline_data[ticker_id].prev_oi = int(contract_details[12])
                    self.parent_app.touchline_data[ticker_id].turnover = float(contract_details[13])
                    self.parent_app.touchline_data[ticker_id].best_bid_price = float(contract_details[14])
                    self.parent_app.touchline_data[ticker_id].best_bid_qty = float(contract_details[15])
                    self.parent_app.touchline_data[ticker_id].best_ask_price = float(contract_details[16])
                    self.parent_app.touchline_data[ticker_id].best_ask_qty = float(contract_details[17])
                    self.parent_app.live_data[ticker_id].populate_using_touchline(self.parent_app.live_data[ticker_id], self.parent_app.touchline_data[ticker_id])
                    if '+' in self.subscription_type:
                        self.parent_app.min_live_data[ticker_id].populate_using_touchline(self.parent_app.min_live_data[ticker_id], self.parent_app.touchline_data[ticker_id])
                self.logger.info(f"Updated touchline data for {symbol} and related live data objects...")
            else:
                self.logger.debug(f'{Style.BRIGHT}{Fore.YELLOW}Probable repeated symbol...{Style.RESET_ALL}')

    def handle_trade_data(self, trade_tick):
        try:
            symbol = self.contract_mapping[int(trade_tick[0])]
            for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                self.parent_app.live_data[ticker_id].symbol_id = int(trade_tick[0])
                self.parent_app.live_data[ticker_id].timestamp = datetime.strptime(trade_tick[1], '%Y-%m-%dT%H:%M:%S')
                self.parent_app.live_data[ticker_id].symbol = symbol
                self.parent_app.live_data[ticker_id].ltp = self.parent_app.touchline_data[ticker_id].ltp = ltp = float(trade_tick[2])
                self.parent_app.live_data[ticker_id].ltq = float(trade_tick[3])
                self.parent_app.live_data[ticker_id].atp = float(trade_tick[4])
                self.parent_app.live_data[ticker_id].ttq = float(trade_tick[5])
                self.parent_app.live_data[ticker_id].day_open = self.parent_app.touchline_data[ticker_id].open = float(trade_tick[6])
                self.parent_app.live_data[ticker_id].day_high = float(trade_tick[7])
                self.parent_app.live_data[ticker_id].day_low = float(trade_tick[8])
                self.parent_app.live_data[ticker_id].prev_day_close = float(trade_tick[9])
                self.parent_app.live_data[ticker_id].oi = int(trade_tick[10])
                self.parent_app.live_data[ticker_id].prev_day_oi = int(trade_tick[11])
                self.parent_app.live_data[ticker_id].turnover = float(trade_tick[12])
                self.parent_app.live_data[ticker_id].special_tag = special_tag = str(trade_tick[13])
                if special_tag != "":
                    if special_tag == 'H':
                        self.parent_app.touchline_data[ticker_id].high = ltp
                    elif special_tag == 'L':
                        self.parent_app.touchline_data[ticker_id].low = ltp
                self.parent_app.live_data[ticker_id].tick_seq = int(trade_tick[14])
                self.parent_app.live_data[ticker_id].tick_type = 1
                try:
                    self.parent_app.live_data[ticker_id].best_bid_price = float(trade_tick[15])
                    self.parent_app.live_data[ticker_id].best_bid_qty = int(trade_tick[16])
                    self.parent_app.live_data[ticker_id].best_ask_price = float(trade_tick[17])
                    self.parent_app.live_data[ticker_id].best_ask_qty = int(trade_tick[18])
                except (IndexError, ValueError, TypeError):
                    try:
                        del self.parent_app.live_data[ticker_id].best_bid_price
                        del self.parent_app.live_data[ticker_id].best_bid_qty
                        del self.parent_app.live_data[ticker_id].best_ask_price
                        del self.parent_app.live_data[ticker_id].best_ask_qty
                    except AttributeError:
                        pass
                except Exception as e:
                    self.logger.error(e)
                if self.trade_callback:
                    try:
                        self.trade_callback(ticker_id, self.parent_app.live_data[ticker_id])
                    except Exception as e:
                        self.logger.error(f'{Style.BRIGHT}{Fore.RED}Encountered error with trade_callback - {type(e)} - {e}{Style.RESET_ALL}')
        except KeyError:
            pass
        except Exception as e:
            self.logger.error(f'{Style.BRIGHT}{Fore.RED}Encountered error with tick feed - {type(e)}{Style.RESET_ALL}')

    def handle_bid_ask_data(self, bidask_tick):
        try:
            symbol = self.contract_mapping[int(bidask_tick[0])]
            for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                self.parent_app.live_data[ticker_id].symbol_id = int(bidask_tick[0])
                self.parent_app.live_data[ticker_id].timestamp = datetime.strptime(bidask_tick[1], '%Y-%m-%dT%H:%M:%S')
                self.parent_app.live_data[ticker_id].best_bid_price = float(bidask_tick[2])
                self.parent_app.live_data[ticker_id].best_bid_qty = int(bidask_tick[3])
                self.parent_app.live_data[ticker_id].best_ask_price = float(bidask_tick[4])
                self.parent_app.live_data[ticker_id].best_ask_qty = int(bidask_tick[5])
                self.parent_app.live_data[ticker_id].tick_type = 2
                if self.bidask_callback:
                    try:
                        self.bidask_callback(ticker_id, self.parent_app.live_data[ticker_id])
                    except Exception as e:
                        self.logger.error(f'{Style.BRIGHT}{Fore.RED}Encountered error with bidask_callback - {type(e)} - {e}{Style.RESET_ALL}')
        except KeyError:
            pass
        except Exception as e:
            self.logger.error(f'{Style.BRIGHT}{Fore.RED}Bid-ask feed error encountered ({type(e)})- {e}{Style.RESET_ALL}')

    def handle_bar_data(self, bar_data):
        try:
            symbol = self.contract_mapping[int(bar_data[0])]
            for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                if '+' in self.subscription_type:
                    obj_to_edit = self.parent_app.min_live_data[ticker_id]
                else:
                    obj_to_edit = self.parent_app.live_data[ticker_id]
                obj_to_edit.symbol_id = int(bar_data[0])
                obj_to_edit.timestamp = datetime.strptime(bar_data[1], '%Y-%m-%dT%H:%M:%S')
                obj_to_edit.symbol = symbol
                obj_to_edit.open = float(bar_data[2])
                obj_to_edit.high = bar_high = float(bar_data[3])
                if bar_high > obj_to_edit.day_high:
                    obj_to_edit.day_high = self.parent_app.touchline_data[ticker_id].high = bar_high
                obj_to_edit.low = bar_low = float(bar_data[4])
                if bar_low < obj_to_edit.day_low:
                    obj_to_edit.day_low = self.parent_app.touchline_data[ticker_id].low = bar_low
                obj_to_edit.close = self.parent_app.touchline_data[ticker_id].ltp = float(bar_data[5])
                obj_to_edit.volume = float(bar_data[6])
                obj_to_edit.oi = float(bar_data[7])
                if self.bar_callback:
                    try:
                        self.bar_callback(ticker_id, obj_to_edit)
                    except Exception as e:
                        self.logger.error(f'{Style.BRIGHT}{Fore.RED}Encountered error with bar_callback - {type(e)} - {e}{Style.RESET_ALL}')
        except KeyError:
            pass
        except Exception as e:
            self.logger.error(f'{Style.BRIGHT}{Fore.RED}Bar feed encountered - {e}{Style.RESET_ALL}')

    def ws_error(self, *args):
        error = args[-1]
        if any(isinstance(error, conn_error) for conn_error in [ConnectionResetError, TimeoutError]):
            self.logger.error(f"Raising WS error = {error}")
            self.last_ping_tm = self.last_pong_tm = 0

    # noinspection PyUnusedLocal
    def ws_open(self, *args):
        self.last_ping_tm = time.time()
        self.sock.ping()
        self.sock.settimeout(15)
        if self.parent_app.symbol_mkt_id_map:
            old_symbol_map = temp_symbol_map = deepcopy(self.parent_app.symbol_mkt_id_map)  # temp_symbol_map is destructed while restarting the data
            temp_symbol_map = dict(temp_symbol_map)
            self.parent_app.symbol_mkt_id_map = defaultdict(set)
            self.logger.debug(f'{list(temp_symbol_map.keys())} needs resuming here.')
            while temp_symbol_map:
                restart_symbols = list(temp_symbol_map.keys())
                restart_req_ids = [temp_symbol_map[symbol].pop() for symbol in restart_symbols]
                self.parent_app.start_live_data(restart_symbols, req_id=restart_req_ids)
                temp_symbol_map = {symbol: symbol_set for (symbol, symbol_set) in temp_symbol_map.items() if symbol_set}
            assert old_symbol_map == self.parent_app.symbol_mkt_id_map
            self.logger.info(f'All streaming symbols have been resumed.')

    # noinspection PyUnusedLocal
    def ws_close(self, *args):
        # self.logger.error('Live WebSocket Closed')
        self.sock.close()
        self.sock = None
        if self.last_ping_tm == 0 == self.last_pong_tm:
            self.logger.debug('DISCONNECTION TYPE(1) FROM SERVER...')
            try:
                time.sleep(1)
                self.run_forever(ping_interval=10, ping_timeout=5)
            except Exception as e:
                self.logger.error(f'{type(e)} in reconnection => {e}')
        if self.last_ping_tm > self.last_pong_tm:
            self.logger.debug('DISCONNECTION TYPE(2) FROM SERVER...')
            try:
                time.sleep(1)
                self.run_forever(ping_interval=10, ping_timeout=5)
            except Exception as e:
                self.logger.error(f'{type(e)} in reconnection2 => {e}')
        # self.logger.error(f'CLOSE: {self.last_ping_tm} -> {self.last_pong_tm}')
