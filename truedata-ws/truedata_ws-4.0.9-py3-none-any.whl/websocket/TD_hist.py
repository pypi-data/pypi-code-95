from .support import historical_decorator, access_token_decorator
from io import StringIO
from datetime import datetime, timedelta
from logging import Logger
from threading import RLock
from colorama import Style, Fore
from typing import List, Dict

import requests
import pandas as pd
import json


class HistoricalREST:
    def __init__(self, login_id: str, password: str, url: str, broker_token: str, logger: Logger):  # NO PORT, broker token needed from now on
        self.login_id = login_id
        self.password = password
        self.url = url
        self.broker_token = broker_token
        self.logger = logger
        self.thread_lock = RLock()
        self.access_token = None
        self.bhavcopy_last_completed = None
        self.access_token_expiry_time = None
        try:
            self.hist_login()
        except Exception as e:
            self.logger.error(f"Failed to connect REST historical API -> {type(e)} = {e}")

    def hist_login(self):
        url_auth = "https://auth.truedata.in/token"
        payload = f"username={self.login_id}&password={self.password}&grant_type=password"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        welcome_msg = requests.request("POST", url_auth, headers=headers, data=payload).text
        welcome_msg = json.loads(welcome_msg)
        try:
            if welcome_msg['access_token']:
                self.access_token = welcome_msg['access_token']
                self.access_token_expiry_time = datetime.now() + timedelta(seconds=welcome_msg['expires_in'] - 15)  # 15 seconds is random buffer time
                self.logger.warning(f"{Style.NORMAL}{Fore.BLUE}Connected successfully to TrueData Historical Data Service... {Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Failed to connect -> {welcome_msg['error_description']}{type(e)} = {e}")
            self.access_token = None

    # noinspection PyUnusedLocal
    @access_token_decorator
    @historical_decorator
    def get_n_historic_bars(self, contract, end_time, no_of_bars, bar_size, options=None, bidask=False):
        source_bar_type_string = 'getlastnbars'
        if 'data_type' not in options.keys():
            options['data_type'] = 'csv'
        try:
            encoded_payload = {
                'symbol': contract,
                'interval': bar_size,
                'response': options['data_type'],
                'bidask': 0
            }
            unencoded_payload = {}
            unencoded_payload = "&".join(unencoded_payload)
            if bar_size == 'tick':
                encoded_payload['nticks'] = no_of_bars
                source_bar_type_string = 'getlastnticks'
                if bidask:
                    encoded_payload['bidask'] = 1
            else:  # Not ticks
                encoded_payload['nbars'] = no_of_bars
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }

            with self.thread_lock:
                url = f"{self.url}/{source_bar_type_string}?{unencoded_payload}"
                response = requests.get(url, headers=headers, params=encoded_payload)
                hist_data = response.text
        except Exception as e:
            self.logger.error(f"{type(e)} -> {e}")
            # json_response = {"success": False, "message": f"({type(e)}) {addn_err_str} -> {e}"}
        hist_data = self.parse_data(hist_data, options)
        return options['processor_to_call'][options['data_type']](hist_data, time_format=options['time_format'])

    @access_token_decorator
    @historical_decorator
    def get_historic_data(self, contract, end_time, start_time, bar_size, options=None, bidask=False):
        source_bar_type_string = 'getbars'
        if 'data_type' not in options.keys():
            options['data_type'] = 'csv'
        try:
            encoded_payload = {
                'symbol': contract,
                'interval': bar_size,
                'response': options['data_type']
            }
            unencoded_payload = {
                f"from={start_time}",
                f"to={end_time}"
            }
            unencoded_payload = "&".join(unencoded_payload)
            if bar_size == 'tick':
                encoded_payload['bidask'] = 0
                source_bar_type_string = 'getticks'
                if bidask:
                    encoded_payload['bidask'] = 1
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            with self.thread_lock:
                url = f"{self.url}/{source_bar_type_string}?{unencoded_payload}"
                response = requests.get(url, headers=headers, params=encoded_payload)
                hist_data = response.text
        except Exception as e:
            self.logger.error(f"{type(e)} -> {e}")
            # json_response = {"success": False, "message": f"({type(e)}) {addn_err_str} -> {e}"}
        hist_data = self.parse_data(hist_data, options)
        return options['processor_to_call'][options['data_type']](hist_data, time_format=options['time_format'])


    def get_gainers_losers(self , segment, topn , gainers , df_style ):
        source_string = "gettopngainers" if gainers else "gettopnlosers"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        payload = {'segment': segment , 'topn': topn , 'response':'csv' }
        url = f"{self.url}/{source_string}?"
        try:
            with self.thread_lock:
                response = requests.get(url, headers=headers , params=payload )
                out = response.text
            df = pd.read_csv(StringIO(out))
            df = df if df_style else list(df.T.to_dict().values())
            df.set_index(["symbol"] , inplace=True) if df_style else 0
        except Exception as e:
            self.logger.error(f"{type(e)} -> No match found for this segment {segment}")
            df = []
        return df


    def parse_data(self, hist_data, options):
        if options['data_type'] == 'csv':
            if hist_data.startswith('"'):
                hist_data = hist_data.split('"')[1]
                if hist_data.startswith('No data exists for') or hist_data.startswith('Symbol does not exist'):
                    self.logger.error(f'{hist_data}')
                    return ''  # Note to devs: Leave this as str to avoid "split" error
            else:
                return hist_data
        else:  # JSON format
            try:
                hist_data = json.loads(hist_data)
            except json.decoder.JSONDecodeError:
                self.logger.error(f'Caught a JSONDecodeError for this request')
                return []
            if hist_data['status'] != 'Success':
                self.logger.error(f"{hist_data['status']}")
                return []
            else:
                return hist_data['Records']

    def bhavcopy_status(self, segment: str):
        url = f'https://history.truedata.in/getbhavcopystatus?segment={segment}&response=csv'
        payload = {}
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        status = response.text.strip().split('\r\n')[-1].split(',')
        assert segment == status[0]
        self.bhavcopy_last_completed = datetime.strptime(status[1], "%Y-%m-%dT%H:%M:%S")

    @access_token_decorator
    def bhavcopy(self, segment: str, date: datetime, return_completed: bool) -> List[Dict]:
        try:
            self.bhavcopy_status(segment)
            if return_completed:
                if date > self.bhavcopy_last_completed:
                    self.logger.error(f"{Style.BRIGHT}{Fore.RED}No complete bhavcopy found for requested date."
                                      f" Last available for {self.bhavcopy_last_completed.strftime('%Y-%m-%d %H:%M:%S')}.{Style.RESET_ALL}")
                    return []
            url_bhavcopy = f"https://history.truedata.in/getbhavcopy?segment={segment}&date={date.strftime('%Y-%m-%d')}&response=csv"
            payload = {}
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.request("GET", url_bhavcopy, headers=headers, data=payload)
            bhavcopy_data = response.text.strip().split('\r\n')
            data_list = []
            # headers = hist_data[0]
            bhavcopy_data = bhavcopy_data[1:]
            for j in bhavcopy_data:
                j = j.split(',')
                data_list.append({'symbol_id': int(j[0]),
                                  'symbol': str(j[1]),
                                  'date': datetime.strptime(str(j[2]), '%Y-%m-%d'),
                                  'o': float(j[3]),
                                  'h': float(j[4]),
                                  'l': float(j[5]),
                                  'c': float(j[6]),
                                  'v': int(j[7]),
                                  'oi': int(j[8])})
            return data_list
        except Exception as e:
            self.logger.error(f"{type(e)} -> {e}")

    @staticmethod
    def hist_json_tick_data_to_dict_list(hist_data, time_format):
        data_list = []
        for j in hist_data:
            try:
                data_list.append({'time': datetime.strptime(j[0], time_format),
                                  'ltp': float(j[1]),
                                  'volume': int(j[2]),
                                  'oi': int(j[3]),
                                  'bid': float(j[4]),
                                  'bid_qty': int(j[5]),
                                  'ask': float(j[6]),
                                  'ask_qty': int(j[7])})
            except IndexError:  # No bid-ask data
                data_list.append({'time': datetime.strptime(j[0], time_format),
                                  'ltp': float(j[1]),
                                  'volume': int(j[2]),
                                  'oi': int(j[3])})
                continue
        return data_list

    @staticmethod
    def hist_json_bar_data_to_dict_list(hist_data, time_format):
        data_list = []
        for j in hist_data:
            data_list.append({'time': datetime.strptime(j[0], time_format),
                              'o': float(j[1]),
                              'h': float(j[2]),
                              'l': float(j[3]),
                              'c': float(j[4]),
                              'v': int(j[5]),
                              'oi': int(j[6])})
        return data_list

    @staticmethod
    def hist_csv_tick_data_to_dict_list(hist_data, time_format):
        hist_data = hist_data.split()
        data_list = []
        # headers = hist_data[0]
        hist_data = hist_data[1:]
        count = 0
        for j in hist_data:
            j = j.split(',')
            try:
                data_list.append({'time': datetime.strptime(j[0], time_format),
                                  'ltp': float(j[1]),
                                  'volume': int(j[2]),
                                  'oi': int(j[3]),
                                  'bid': float(j[4]),
                                  'bid_qty': int(j[5]),
                                  'ask': float(j[6]),
                                  'ask_qty': int(j[7])})
            except IndexError:  # No bid-ask data
                data_list.append({'time': datetime.strptime(j[0], time_format),
                                  'ltp': float(j[1]),
                                  'volume': int(j[2]),
                                  'oi': int(j[3])})
                continue
            count = count + 1
        return data_list

    @staticmethod
    def hist_csv_bar_data_to_dict_list(hist_data, time_format):
        hist_data = hist_data.split()
        data_list = []
        # headers = hist_data[0]
        hist_data = hist_data[1:]
        for j in hist_data:
            j = j.split(',')
            # time_format = '%Y-%m-%dT%H:%M:%S'
            data_list.append({'time': datetime.strptime(j[0], time_format),
                              'o': float(j[1]),
                              'h': float(j[2]),
                              'l': float(j[3]),
                              'c': float(j[4]),
                              'v': int(j[5]),
                              'oi': int(j[6])})
        return data_list
