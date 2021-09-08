import datetime
import os
import re
import xml

import xml.dom.minidom

from SapphireQuant.Config.TradingFrame.TradingFrameHelper import TradingFrameHelper
from SapphireQuant.Core.Futures import FutureExchange
from SapphireQuant.Core.Futures.Future import Future
from SapphireQuant.Core.Futures.FutureProduct import FutureProduct


class FutureManager:
    """
    期货合约管理
    """
    FileName = 'future.xml'
    HisFileName = 'HisFutures.xml'
    DefaultExchangeMap = {
        'CFFEX': ['中国金融交易所', '9:00,10:15,10:30,11:30,13:30,15:00'],
        'SHFE': ['上海期货交易所', '9:00,10:15,10:30,11:30,13:30,15:00'],
        'DCE': ['大连商品交易所', '9:00,10:15,10:30,11:30,13:30,15:00'],
        'CZCE': ['郑州商品交易所', '9:00,10:15,10:30,11:30,13:30,15:00'],
        'SGX': ['新加坡交易所', '9:00,10:15,10:30,11:30,13:30,15:00'],
        'SGE': ['上海黄金交易所', '9:00,10:15,10:30,11:30,13:30,15:00'],
        'INE': ['能源所', '9:00,10:15,10:30,11:30,13:30,15:00'],
    }

    # DefaultProductMap = {
    #     # CFFEX
    #     'IF': '沪深300指数',
    #     'IC': '中证500指数',
    #     'IH': '上证50指数',
    #     'T': '10年期国债',
    #     'TF': '5年期国债',
    #     'TS': '2年期国债',
    #
    #     # SHFE
    #     'ru': '天然橡胶',
    #     'cu': '沪铜',
    #     'zn': '沪锌',
    #     'ni': '沪镍',
    #     'sn': '沪锡',
    #     'rb': '螺纹钢',
    #     'hc': '热轧卷',
    #     'bu': '沥青',
    #     'au': '黄金',
    #     'ag': '白银',
    #     'al': '沪铝',
    #     'pb': '沪铅',
    #     'wr': '线材',
    #     'fu': '燃料油',
    #     'sp': '纸浆',
    #     'ss': '不锈钢',
    #
    #     # DCE
    #     'c': '玉米',
    #     'cs': '玉米淀粉',
    #     'a': '豆一',
    #     'b': '豆二',
    #     'm': '豆粕',
    #     'y': '豆油',
    #     'p': '棕榈油',
    #     'jd': '鸡蛋',
    #     'bb': '胶合板',
    #     'fb': '纤维板',
    #     'l': '聚乙烯',
    #     'v': '聚氯乙烯',
    #     'pp': '聚丙烯',
    #     'j': '焦炭',
    #     'jm': '焦煤',
    #     'i': '铁矿石',
    #     'eg': '乙二醇',
    #     'rr': '粳米',
    #     'eb': '苯乙烯',
    #
    #     #CZCE
    #     'WH': '强麦',
    #     'WH': '强麦',
    # }

    DefaultFutureMap = {
        '9999': '主力合约',
        '9991': '次主力合约',
        '9998': '当月连续',
        '9997': '下月连续',
        '9996': '下季连续',
        '9995': '隔季连续',
        '9990': '指数合约',
    }

    def __init__(self):
        self.__all_exchanges = {}
        self.__all_products = {}
        self.__all_futures = {}
        self.__is_loaded = False
        self.__path = ""
        self.__history_path = ""

    @property
    def all_exchanges(self):
        """
        所有交易市场列表
        :return:
        """
        return self.__all_exchanges

    @property
    def all_products(self):
        """
        所有期货产品列表
        :return:
        """
        return self.__all_products

    @property
    def all_instruments(self):
        """
        所有期货合约列表
        :return:
        """
        return self.__all_futures

    def __getitem__(self, item):
        if item.id in self.__all_futures.keys():
            return self.__all_futures[item.id]
        return None

    def load(self, config_directory, load_history=True):
        """
        加载配置文件
        :param load_history:
        :param config_directory:
        """
        if not self.__is_loaded:
            self.load_future(config_directory)
            if load_history:
                self.load_his_future(config_directory)

    def load_future(self, config_directory):
        """
        加载期货Xml
        :param config_directory:
        """
        try:
            self.__path = os.path.join(config_directory, self.FileName)
            self.__history_path = os.path.join(config_directory, self.HisFileName)
            if os.path.exists(self.__path):
                pass
            else:
                print("未找到配置文件:" + self.__path)
            _root = xml.dom.minidom.parse(self.__path).documentElement
            exchange_nodes = _root.getElementsByTagName('Exchange')
            for exchange_node in exchange_nodes:
                self.__read_exchange(exchange_node)

            self.__is_loaded = True
        except Exception as e:
            print(str(e))

    def load_his_future(self, config_directory):
        """
        加载历史期货Xml
        :param config_directory:
        """
        try:
            self.__path = os.path.join(config_directory, self.FileName)
            self.__history_path = os.path.join(config_directory, self.HisFileName)
            if os.path.exists(self.__history_path):
                pass
            else:
                print("未找到配置文件:" + self.__history_path)
            _root = xml.dom.minidom.parse(self.__history_path).documentElement
            exchange_nodes = _root.getElementsByTagName('Exchange')
            for exchange_node in exchange_nodes:
                self.__read_exchange(exchange_node)

            self.__is_loaded = True
        except Exception as e:
            print(str(e))

    def __read_exchange(self, exchange_node):
        exchange = FutureExchange()
        exchange.exchange_id = exchange_node.getAttribute('id')
        exchange.exchange_name = exchange_node.getAttribute('name')

        trading_time_nodes = exchange_node.getElementsByTagName('TradingTime')
        trading_time = self.get_node_value(trading_time_nodes[0])
        exchange.all_slice = TradingFrameHelper.parse_time_slice(trading_time)
        # trading_time_arr = trading_time.split(',')
        # count = len(trading_time_arr) / 2
        # for i in range(int(count)):
        #     time_slice = TimeSlice()
        #     time_slice.begin_time = TradingFrameHelper.str_pares_timedelta(trading_time_arr[i * 2])
        #     time_slice.end_time = TradingFrameHelper.str_pares_timedelta(trading_time_arr[i * 2 + 1])
        #
        #     exchange.all_slice.append(time_slice)

        open_time_nodes = exchange_node.getElementsByTagName('OpenTime')
        open_timedelta = TradingFrameHelper.str_pares_timedelta(self.get_node_value(open_time_nodes[0]))
        exchange.open_time = datetime.date.today() + open_timedelta

        close_time_nodes = exchange_node.getElementsByTagName('CloseTime')
        close_timedelta = TradingFrameHelper.str_pares_timedelta(self.get_node_value(close_time_nodes[0]))
        exchange.close_time = datetime.date.today() + close_timedelta

        self.__add_exchange(exchange)

        product_nodes = exchange_node.getElementsByTagName('Product')
        for product_node in product_nodes:
            self.__read_product(product_node, exchange.exchange_id)

    def __read_product(self, product_node, exchange_id):
        product = FutureProduct()
        product.product_id = product_node.getAttribute('id')
        product.product_name = product_node.getAttribute('name')
        product.exchange_id = exchange_id

        if product.product_id != "":
            self.__add_product(product)

        future_nodes = product_node.getElementsByTagName('Future')
        for future_node in future_nodes:
            future = self.__read_future(future_node)
            future_id = future.id
            if (future_id.find("9995") > 0) | (future_id.find("9996") > 0) | (future_id.find("9997") > 0) | (future_id.find("9998") > 0) | (
                    future_id.find("9999") > 0):
                future.real_future = future

            if future.id != "":
                future.exchange_id = product.exchange_id
                future.product_id = product.product_id

                self.__add_future(future)

    def __read_future(self, future_node):
        future = Future()
        future.id = future_node.getAttribute('id')
        future.name = future_node.getAttribute('name')

        product_id_nodes = future_node.getElementsByTagName('ProductID')
        future.product_id = self.get_node_value(product_id_nodes[0])

        exchange_id_nodes = future_node.getElementsByTagName('ExchangeID')
        future.exchange_id = self.get_node_value(exchange_id_nodes[0])

        open_date_nodes = future_node.getElementsByTagName('OpenDate')
        future.open_date = datetime.datetime.strptime(self.get_node_value(open_date_nodes[0]), '%Y/%m/%d %H:%M:%S')

        expire_date_nodes = future_node.getElementsByTagName('ExpireDate')
        future.expire_date = datetime.datetime.strptime(self.get_node_value(expire_date_nodes[0]), '%Y/%m/%d %H:%M:%S')

        long_margin_ratio_nodes = future_node.getElementsByTagName('LongMarginRatio')
        future.long_margin_ratio = float(self.get_node_value(long_margin_ratio_nodes[0]))

        short_margin_ratio_nodes = future_node.getElementsByTagName('ShortMarginRatio')
        future.short_margin_ratio = float(self.get_node_value(short_margin_ratio_nodes[0]))

        volume_multiple_nodes = future_node.getElementsByTagName('VolumeMultiple')
        future.volume_multiple = int(self.get_node_value(volume_multiple_nodes[0]))

        price_tick_nodes = future_node.getElementsByTagName('PriceTick')
        future.price_tick = float(self.get_node_value(price_tick_nodes[0]))

        return future

    @staticmethod
    def get_node_value(node):
        """
        获取节点的值
        :param node:
        :return:
        """
        return node.firstChild.data

    def __add_exchange(self, exchange):
        if exchange.exchange_id in self.__all_exchanges.keys():
            return

        self.__all_exchanges[exchange.exchange_id] = exchange

        # print(exchange.to_string())

    def __add_product(self, product):
        if product.product_id in self.__all_products.keys():
            return

        self.__all_products[product.product_id] = product

        if product.exchange_id in self.__all_exchanges.keys():
            exchange = self.__all_exchanges[product.exchange_id]
            if product.product_id not in exchange.product_map.keys():
                exchange.products.append(product)
                exchange.product_map[product.product_id] = product

        # print(product.to_string())

    def __add_future(self, future):
        if future is None:
            return

        if future.id in self.__all_futures.keys():
            return

        self.__all_futures[future.id] = future

        if future.product_id in self.__all_products.keys():
            product = self.__all_products[future.product_id]
            if future.id not in product.future_map.keys():
                product.futures.append(future)
                product.future_map[future.id] = future

        # print(future.to_string())

    @staticmethod
    def get_default_exchanges():
        """
        获取默认的Exchange
        """
        dic_exchanges = {}
        for key in FutureManager.DefaultExchangeMap.keys():
            exchange = FutureExchange()
            exchange.exchange_id = key
            exchange.exchange_name = FutureManager.DefaultExchangeMap[key][0]
            trading_time = FutureManager.DefaultExchangeMap[key][1]
            exchange.all_slice = TradingFrameHelper.parse_time_slice(trading_time)
            exchange.open_time = exchange.all_slice[0].begin_time
            exchange.close_time = exchange.all_slice[-1].end_time
            dic_exchanges[key] = exchange
        return dic_exchanges

    @staticmethod
    def get_default_futures():
        """
        获取默认的Future
        """
        dic_futures = {}
        for key in FutureManager.DefaultFutureMap.keys():
            future = Future()
            future.id = key
            future.name = FutureManager.DefaultFutureMap[key]
            future.product_id = None
            future.exchange_id = None
            future.open_date = datetime.datetime.min
            future.expire_date = datetime.datetime.max
            future.long_margin_ratio = 0
            future.short_margin_ratio = 0
            future.volume_multiple = 0
            future.price_tick = 0
            dic_futures[key] = future

    def update(self, lst_futures):
        """
        更新期货列表
        :param lst_futures:
        """
        history_exchanges = FutureManager.get_default_exchanges()
        today_exchanges = FutureManager.get_default_exchanges()
        lst_today_future_id = list(map(lambda x: x.id, lst_futures))
        # 原有期货品种分成历史和当日
        for future_id in self.__all_futures.keys():
            default_id = re.sub(r"[a-zA-Z]", "", future_id, 0)
            if default_id in FutureManager.DefaultFutureMap.keys():
                continue
            future = self.__all_futures[future_id]
            target_exchange = None
            if future_id in lst_today_future_id:
                if future.exchange_id in today_exchanges.keys():
                    target_exchange = today_exchanges[future.exchange_id]
                else:
                    print('非法的交易市场ID:{0}'.format(future.exchange_id))
            else:
                if future.exchange_id in history_exchanges.keys():
                    target_exchange = history_exchanges[future.exchange_id]
                else:
                    print('非法的交易市场ID:{0}'.format(future.exchange_id))

            if target_exchange is not None:
                if future.product_id in target_exchange.product_map.keys():
                    product = target_exchange.product_map[future.product_id]
                else:
                    product = FutureProduct()
                    product.product_id = future.product_id
                    product.product_name = re.sub(r'[0-9]*$', '', future.name, 0)
                    target_exchange.product_map[future.product_id] = product
                    target_exchange.products.append(product)
                if future_id in product.future_map.keys():
                    product.future_map[future_id] = future
                else:
                    product.future_map[future_id] = future
                    product.futures.append(future)

        for future in lst_futures:
            if future.exchange_id in today_exchanges.keys():
                exchange = today_exchanges[future.exchange_id]
            else:
                exhcange = FutureExchange()
                exchange.exchange_id = future.exchange_id
                exchange.exchange_name = future.exchange_id
                today_exchanges[exchange.exchange_id] = exchange
            if future.product_id in exchange.product_map.keys():
                product = exchange.product_map[future.product_id]
            else:
                product = FutureProduct()
                product.product_id = future.product_id
                product.exchange_id = future.exchange_id
                product.product_name = future.product_id
                exchange.product_map[product.product_id] = product
                exchange.products.append(product)

            if future.id not in product.future_map.keys():
                product.future_map[future.id] = future
                product.futures.append(future)

        for exchange in today_exchanges.values():
            for product in exchange.products:
                for custom_id in FutureManager.DefaultFutureMap.keys():
                    custom_future = Future()
                    custom_future.exchange_id = exchange.exchange_id
                    custom_future.product_id = product.product_id
                    custom_future.id = '{0}{1}'.format(product.product_id, custom_id)
                    custom_future.name = '{0}{1}'.format(product.product_name, FutureManager.DefaultFutureMap[custom_id])
                    if len(product.futures) > 0:
                        product.futures.sort(key=lambda x: x.expire_date, reverse=True)
                        future = product.futures[0]
                        custom_future.expire_date = future.expire_date
                        custom_future.open_date = future.open_date
                        custom_future.long_margin_ratio = future.long_margin_ratio
                        custom_future.short_margin_ratio = future.short_margin_ratio
                        custom_future.volume_multiple = future.volume_multiple
                        custom_future.price_tick = future.price_tick
                        product.futures.append(custom_future)
                        product.future_map[custom_future.id] = custom_future

        FutureManager.save_xml(today_exchanges, self.__path)
        FutureManager.save_xml(history_exchanges, self.__history_path)

    @staticmethod
    def save_xml(exchanges, file_path):
        """
        保存文件
        :param exchanges:
        :param file_path:
        """
        dom = xml.dom.minidom.getDOMImplementation().createDocument(None, 'Ats', None)
        root = dom.documentElement
        lst_exchange = list(exchanges.values())
        lst_exchange.sort(key=lambda x: x.exchange_id)
        for exchange in lst_exchange:
            exchange_element = dom.createElement('Exchange')
            exchange_element.setAttribute('id', str(exchange.exchange_id))
            exchange_element.setAttribute('name', str(exchange.exchange_name))
            exchange_element.setAttribute('count', str(len(exchange.products)))

            trading_time = ''
            for time_slice in exchange.all_slice:
                trading_time = '{0},{1},{2}'.format(trading_time, str(time_slice.begin_time), str(time_slice.end_time))
            trading_time = trading_time[1:]
            open_time = str(exchange.all_slice[0].begin_time)
            close_time = str(exchange.all_slice[-1].end_time)
            trading_time_element = dom.createElement('TradingTime')
            trading_time_element.appendChild(dom.createTextNode(trading_time))
            open_time_element = dom.createElement('OpenTime')
            open_time_element.appendChild(dom.createTextNode(open_time))
            close_time_element = dom.createElement('CloseTime')
            close_time_element.appendChild(dom.createTextNode(close_time))
            exchange_element.appendChild(trading_time_element)
            exchange_element.appendChild(open_time_element)
            exchange_element.appendChild(close_time_element)

            lst_product = exchange.products
            lst_product.sort(key=lambda x: x.product_id)
            for product in lst_product:
                product_element = dom.createElement('Product')
                product_element.setAttribute('id', str(product.product_id))
                product_element.setAttribute('name', str(product.product_name))
                exchange_element.appendChild(product_element)

                lst_future = product.futures
                lst_future.sort(key=lambda x: x.id, reverse=True)
                for future in lst_future:
                    future_element = dom.createElement('Future')
                    future_element.setAttribute('id', future.id)
                    future_element.setAttribute('name', future.name)

                    future_exchange_element = dom.createElement('ExchangeID')
                    future_exchange_element.appendChild(dom.createTextNode(future.exchange_id))

                    future_expire_date_element = dom.createElement('ExpireDate')
                    future_expire_date_element.appendChild(dom.createTextNode(future.expire_date.strftime('%Y/%m/%d %H:%M:%S')))

                    future_long_margin_ratio_element = dom.createElement('LongMarginRatio')
                    future_long_margin_ratio_element.appendChild(dom.createTextNode(str(future.long_margin_ratio)))

                    future_open_date_element = dom.createElement('OpenDate')
                    future_open_date_element.appendChild(dom.createTextNode(future.open_date.strftime('%Y/%m/%d %H:%M:%S')))

                    future_product_id_element = dom.createElement('ProductID')
                    future_product_id_element.appendChild(dom.createTextNode(future.product_id))

                    future_short_margin_ratio_element = dom.createElement('ShortMarginRatio')
                    future_short_margin_ratio_element.appendChild(dom.createTextNode(str(future.short_margin_ratio)))

                    future_volume_multiple_element = dom.createElement('VolumeMultiple')
                    future_volume_multiple_element.appendChild(dom.createTextNode(str(future.volume_multiple)))

                    future_price_tick_element = dom.createElement('PriceTick')
                    future_price_tick_element.appendChild(dom.createTextNode(str(future.price_tick)))

                    future_element.appendChild(future_exchange_element)
                    future_element.appendChild(future_expire_date_element)
                    future_element.appendChild(future_long_margin_ratio_element)
                    future_element.appendChild(future_open_date_element)
                    future_element.appendChild(future_product_id_element)
                    future_element.appendChild(future_short_margin_ratio_element)
                    future_element.appendChild(future_volume_multiple_element)
                    future_element.appendChild(future_price_tick_element)
                    product_element.appendChild(future_element)

            root.appendChild(exchange_element)

        with open(file_path, 'w', encoding='utf-8') as f:
            dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')

# future_manager = FutureManager()
# config_dir = os.path.join(sys.modules["ROOT_DIR"], 'Profiles')
# future_manager.load(config_dir, load_history=False)
# lst_futures = future_manager.all_products['IF'].futures
# future_manager.update(lst_futures)
# for data in future_manager.all_instruments.values():
#     print(data.to_string())
# print(re.sub(r'[0-9]*$', '', '沪深300指数2008', 0))
