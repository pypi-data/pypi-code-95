import datetime
import os
import re
import xml

import xml.dom.minidom


from SapphireQuant.Config.TradingFrame.FutureProductTradingFrame import FutureProductTradingFrame
from SapphireQuant.Config.TradingFrame.FutureExchangeTradingFrame import FutureExchangeTradingFrame
from SapphireQuant.Config.TradingFrame.FutureTradingFrame import FutureTradingFrame
from SapphireQuant.Config.TradingFrame.LimitValue import LimitValue
from SapphireQuant.Config.TradingFrame.TradingFrameNode import TradingFrameNode
from SapphireQuant.Core.Enum.EnumMarket import EnumMarket
from SapphireQuant.Core.TimeSlice import TimeSlice


class TradingFrameManager:
    """
    交易时间框架管理
    """
    FileName = "TradingFrame.xml"

    def __init__(self):
        self.__is_loaded = False
        self.__path = ""
        self.__future = None
        self.__future_trading_time_map = {}
        self.__default_frame = []
        self.__default_future_trading_time_map = {}

    @property
    def future(self):
        """
        期货交易时间
        :return:
        """
        return self.__future

    def load(self, config_directory):
        """
        加载配置
        :param config_directory:
        """
        if not self.__is_loaded:
            try:
                self.__path = os.path.join(config_directory, self.FileName)
                if os.path.exists(self.__path):
                    pass
                else:
                    print("未找到配置文件:" + self.__path)

                _root = xml.dom.minidom.parse(self.__path).documentElement
                future_nodes = _root.getElementsByTagName('Future')
                for future_node in future_nodes:
                    self.__future = TradingFrameManager.__read_future_trading_frame(future_node)

                self.__default_frame = []
                time_slice_am = TimeSlice()
                time_slice_am.begin_time = datetime.timedelta(hours=9, minutes=30, seconds=0)
                time_slice_am.end_time = datetime.timedelta(hours=11, minutes=30, seconds=0)
                self.__default_frame.append(time_slice_am)

                time_slice_pm = TimeSlice()
                time_slice_pm.begin_time = datetime.timedelta(hours=13, minutes=0, seconds=0)
                time_slice_pm.end_time = datetime.timedelta(hours=15, minutes=0, seconds=0)
                self.__default_frame.append(time_slice_pm)

                self.__default_future_trading_time_map = {}
                self.__future_trading_time_map = {}

                for exchange in self.__future.exchanges:
                    self.__default_future_trading_time_map[exchange.id] = exchange.trading_time_slices

                    for product in exchange.products:
                        self.__future_trading_time_map[product.id] = product.trading_frames

                self.__is_loaded = True
            except Exception as e:
                print(str(e))
        pass

    def get_trading_time_slices(self, trading_date, market, exchange_id, product_id=""):
        """
        获取指定交易日的交易时间区间TimeSlice
        :param trading_date:
        :param market:
        :param exchange_id:
        :param product_id:
        :return:
        """
        if trading_date is None:
            return self.get_last_trading_time_slices(market, exchange_id, product_id)

        trading_frame_slices = self.get_trading_time_frames(market, exchange_id, product_id)

        lst_time_slices = None
        i = len(trading_frame_slices) - 1
        while i >= 0:
            trading_frame = trading_frame_slices[i]
            begin_day = trading_frame.begin_day

            if trading_date >= begin_day:
                lst_time_slices = trading_frame.trading_time_slices
                break

            i -= 1

        if lst_time_slices is not None:
            return lst_time_slices

        return self.get_default_trading_time_slices(market, exchange_id)

    def get_default_trading_time_slices(self, market, exchange_id):
        """
        获取默认的TimeSlice
        :param market:
        :param exchange_id:
        :return:
        """
        if market == EnumMarket.期货:
            if exchange_id in self.__default_future_trading_time_map.keys():
                return self.__default_future_trading_time_map[exchange_id]

    def get_last_trading_time_slices(self, market, exchange_id, product_id=""):
        """
        获取最后一个TimeSlice
        :param market:
        :param exchange_id:
        :param product_id:
        :return:
        """
        time_frame_series = self.get_trading_time_frames(market, exchange_id, product_id)

        if time_frame_series is not None:
            return time_frame_series[-1].trading_time_slices

    def get_trading_time_frames(self, market, exchange_id, product_id=""):
        """
        获取交易时间
        :param market:
        :param exchange_id:
        :param product_id:
        :return:
        """
        if market == EnumMarket.期货:
            if product_id in self.__future_trading_time_map.keys():
                return self.__future_trading_time_map[product_id]
        return None

    def get_living_time(self, trading_day, market, exchange_id, product_id=""):
        """
        根据交易日 获取当日的开盘收盘时间的TimeSlice
        :param trading_day:
        :param market:
        :param exchange_id:
        :param product_id:
        :return:
        """
        lst_time_slices = self.get_trading_time_slices(trading_day, market, exchange_id, product_id)

        if (lst_time_slices is not None) & (len(lst_time_slices) > 0):
            time_slices = TimeSlice()
            time_slices.begin_time = lst_time_slices[0].begin_time
            time_slices.end_time = lst_time_slices[-1].end_time
            return time_slices

        return None

    def get_open_time(self, trading_day, market, exchange_id, product_id=""):
        """
        获取当日开盘时间
        :param trading_day:
        :param market:
        :param exchange_id:
        :param product_id:
        :return:
        """
        lst_time_slices = self.get_trading_time_slices(trading_day, market, exchange_id, product_id)

        if (lst_time_slices is not None) & (len(lst_time_slices) > 0):
            return lst_time_slices[0].begin_time

        return None

    def get_close_time(self, trading_day, market, exchange_id, product_id=""):
        """
        获取当日收盘时间
        :param trading_day:
        :param market:
        :param exchange_id:
        :param product_id:
        :return:
        """
        lst_time_slices = self.get_trading_time_slices(trading_day, market, exchange_id, product_id)

        if (lst_time_slices is not None) & (len(lst_time_slices) > 0):
            return lst_time_slices[-1].end_time

        return None

    def get_listing_date(self, market, exchange_id, instrument_id):
        """
        获取上市日期
        """
        product_id = re.sub(r"\d", "", instrument_id, 0)
        lst_data = self.get_trading_time_frames(market, exchange_id, product_id)
        if lst_data is None:
            return None
        lst_data.sort(key=lambda x: x.begin_day)
        if len(lst_data) >= 1:
            return lst_data[1].begin_day
        else:
            return None

    def get_active_date(self, market, exchange_id, instrument_id):
        """
        获取活跃日期
        """
        product_id = re.sub(r"\d", "", instrument_id, 0)
        lst_data = self.get_trading_time_frames(market, exchange_id, product_id)
        if lst_data is None:
            return None
        lst_data.sort(key=lambda x: x.begin_day)
        if product_id == 'fu':
            return datetime.datetime(2018, 7, 17)
        else:
            if len(lst_data) >= 1:
                return lst_data[1].begin_day
            else:
                return None

    def get_product_ids(self, market, exchange_id):
        """
        获取产品ID
        :param market:
        :param exchange_id:
        :return:
        """
        lst_product_id = []
        if market == EnumMarket.期货:
            for exchange in self.__future.exchanges:
                if exchange.id == exchange_id:
                    for product in exchange.products:
                        lst_product_id.append(product.id)

        return lst_product_id

    def get_all_product_ids(self, market):
        """
        获取产品ID
        :param market:
        :return:
        """
        lst_product_id = []
        if market == EnumMarket.期货:
            for exchange in self.__future.exchanges:
                for product in exchange.products:
                    lst_product_id.append(product.id)

        return lst_product_id

    @staticmethod
    def __read_future_trading_frame(node):
        future_trading_frame = FutureTradingFrame()
        future_trading_frame.exchanges = []
        exchange_nodes = node.getElementsByTagName('Exchange')
        for exchange_node in exchange_nodes:
            exchange_trading_frame = TradingFrameManager.__read_future_exchange_trading_frame(exchange_node)
            future_trading_frame.exchanges.append(exchange_trading_frame)
        return future_trading_frame

    @staticmethod
    def __read_future_exchange_trading_frame(node):
        future_exchange_trading_frame = FutureExchangeTradingFrame()
        future_exchange_trading_frame.id = node.getAttribute('id')
        future_exchange_trading_frame.name = node.getAttribute('name')
        future_exchange_trading_frame.trading_time = node.getAttribute('TradingTime')
        future_exchange_trading_frame.products = []
        products_nodes = node.getElementsByTagName('Products')
        for products_node in products_nodes:
            product_nodes = products_node.getElementsByTagName('Product')
            for product_node in product_nodes:
                product_trading_frame = TradingFrameManager.__read_product_trading_frame(product_node)
                future_exchange_trading_frame.products.append(product_trading_frame)
        return future_exchange_trading_frame

    @staticmethod
    def __read_product_trading_frame(node):
        product_trading_frame = FutureProductTradingFrame()
        product_trading_frame.id = node.getAttribute('id')
        product_trading_frame.name = node.getAttribute('name')
        trading_frame_nodes = node.getElementsByTagName('TradingFrame')
        product_trading_frame.trading_frames = []
        for trading_frame_node in trading_frame_nodes:
            trading_frame = TradingFrameNode()
            trading_frame.begin_day_string = trading_frame_node.getAttribute('BeginDay')
            trading_frame.trading_time = trading_frame_node.getAttribute('TradingTime')
            product_trading_frame.trading_frames.append(trading_frame)

        limit_value_nodes = node.getElementsByTagName('LimitValue')
        for limit_value_node in limit_value_nodes:
            product_trading_frame.limit_value = LimitValue()
            product_trading_frame.limit_value.up_limit = float(limit_value_node.getAttribute('UpLimit'))
            product_trading_frame.limit_value.low_limit = float(limit_value_node.getAttribute('LowLimit'))

        return product_trading_frame


# trading_frame_manager = TradingFrameManager()
# config_dir = os.path.join(sys.modules['ROOT_DIR'], 'Profiles')
# trading_frame_manager.load(config_dir)
# index = 0
# exchange_index_map = {}
# exchange_product_id_map = {}
# for exchange in trading_frame_manager.future.exchanges:
#     print(exchange.id + ":" + exchange.name + ":" + exchange.trading_time)
#     exchange_index = 0
#     exchange_products = ""
#     for product in exchange.products:
#         print(product.id + ":" + product.name)
#         for trading_frame in product.trading_frames:
#             print("TradingFrameNode:BeginDay=" + trading_frame.begin_day_string + ",TradingTime=" + trading_frame.trading_time)
#         print("LimitValue:" + str(product.limit_value.up_limit) + "," + str(product.limit_value.low_limit))
#         index += 1
#         exchange_index += 1
#         exchange_products += product.id + ";"
#
#     exchange_index_map[exchange.id] = exchange_index
#     exchange_product_id_map[exchange.id] = exchange_products
# print("共计" + str(index) + "个品种")
# for data in exchange_index_map.keys():
#     print(data + ":" + str(exchange_index_map[data]) + "个品种:" + exchange_product_id_map[data])
#
# market = EnumMarket.期货
# exchange_id = "CFFEX"
# product_id = "IF"
# trading_date = datetime.datetime(2019, 10, 8)
# lst_time_slices = trading_frame_manager.get_trading_time_slices(trading_date, market, exchange_id, product_id)
# print("GetTradingTimeSlices:"+exchange_id+","+product_id+","+trading_date.strftime("%Y/%m%d"))
# for time_slice in lst_time_slices:
#     print("BeginTime:"+time_slice.to_string())
#     print("EndTime:"+time_slice.to_string())
#
# default_trading_time_slices = trading_frame_manager.get_default_trading_time_slices(market, exchange_id)
# print("GetDefaultTradingTimeSlices:"+exchange_id)
# for time_slice in default_trading_time_slices:
#     print("BeginTime:"+time_slice.to_string())
#     print("EndTime:"+time_slice.to_string())
#
# last_trading_time_slices = trading_frame_manager.get_last_trading_time_slices(market, exchange_id, product_id)
# print("GetLastTradingTimeSlices:"+exchange_id)
# for time_slice in last_trading_time_slices:
#     print("BeginTime:"+time_slice.to_string())
#     print("EndTime:"+time_slice.to_string())
#
# trading_time_frames = trading_frame_manager.get_trading_time_frames(market, exchange_id, product_id)
# print("GetTradingTimeFrames:"+exchange_id+","+product_id)
# for trading_frame in trading_time_frames:
#     print("BeginDay:"+trading_frame.begin_day.strftime("%Y/%m/%d"))
#     print("TradingTime:"+trading_frame.trading_time)
#
# living_time = trading_frame_manager.get_living_time(trading_date, market, exchange_id, product_id)
# print("GetLivingTime:"+exchange_id+","+product_id+","+trading_date.strftime("%Y/%m/%d"))
# print("TradingTime:"+living_time.to_string())
#
# open_time = trading_frame_manager.get_open_time(trading_date, market, exchange_id, product_id)
# print("GetOpenTime:"+exchange_id+","+product_id+","+trading_date.strftime("%Y/%m/%d"))
# print("TradingTime:"+str(open_time))
#
# close_time = trading_frame_manager.get_close_time(trading_date, market, exchange_id, product_id)
# print("GetCloseTime:"+exchange_id+","+product_id+","+trading_date.strftime("%Y/%m/%d"))
# print("TradingTime:"+str(close_time))