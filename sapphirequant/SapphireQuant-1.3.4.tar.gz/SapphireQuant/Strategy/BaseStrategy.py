import abc
import datetime
import os
import uuid

from SapphireQuant.DataStorage.Cache.FutureCache import EnumLiquidationType
from SapphireQuant.Lib import FileToolBox


class BaseStrategy:
    """
    策略基类
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.function = kwargs['function']
        if 'mongodb_client' in kwargs.keys():
            self.mongodb_client = kwargs['mongodb_client']
        else:
            self.mongodb_client = None
        self.record_dir = kwargs['record_dir']
        self.product_code = kwargs['product_code']
        self.strategy_id = kwargs['strategy_id']
        self.drive_code = kwargs['drive_code']
        self.subscribe_futures = kwargs['future_codes']

        self.start_simulate_date = kwargs['start_simulate_date']
        self.end_simulate_date = kwargs['end_simulate_date']
        self.trading_date = self.start_simulate_date
        self.data_handler = kwargs['data_handler']
        self.fund_balance = kwargs['fund_balance']
        self.instrument_manager = self.data_handler.instrument_manager
        self.transaction_rate = kwargs['transaction_rate']
        self.long_margin_rate = kwargs['long_margin_rate']
        self.short_margin_rate = kwargs['short_margin_rate']

        self.liquidation_type = EnumLiquidationType.收盘价
        if 'liquidation_type' in kwargs.keys():
            self.liquidation_type = kwargs['liquidation_type']

        self.future_cache = kwargs['future_cache']

    @property
    def tick_now(self):
        """

        :return:
        """
        return self.function.now

    @property
    def df_asset(self):
        """

        :return:
        """
        return self.function.df_asset

    @property
    def df_order(self):
        """

        :return:
        """
        return self.function.df_order

    @property
    def df_trade(self):
        """

        :return:
        """
        return self.function.df_trade

    @property
    def df_position(self):
        """

        :return:
        """
        return self.function.df_position

    @property
    def df_summary(self):
        """

        :return:
        """
        return self.function.df_summary

    @property
    def all_futures(self):
        """

        :return:
        """
        return self.function.all_futures

    @property
    def last_bar_map(self):
        """

        :return:
        """
        return self.function.last_bar_map

    def add_indicator(self, indicator):
        """
        添加指标
        :param indicator:
        """
        self.function.add_indicator(indicator)

    def send_order(self, instrument_id, direction, open_close, volume, price, order_time=None):
        """
        发送委托
        :param order_time:
        :param instrument_id:
        :param direction:
        :param open_close:
        :param volume:
        :param price:
        """
        if order_time is None:
            if instrument_id in self.last_bar_map.keys():
                last_bar = self.last_bar_map[instrument_id]
                if last_bar is not None:
                    if last_bar.open == price:
                        order_time = last_bar.begin_time
                    elif last_bar.close == price:
                        order_time = last_bar.end_time
                    else:
                        order_time = self.tick_now
                else:
                    order_time = self.tick_now

        order = self.function.send_future_order('', uuid.uuid1(), self.product_code, self.strategy_id,
                                                instrument_id, 'exchange_id', price, volume, direction, open_close, order_time=order_time)
        return order

    @abc.abstractmethod
    def on_start(self):
        """
        回测开始
        """
        pass

    @abc.abstractmethod
    def on_init(self):
        """
        初始化
        """
        pass

    @abc.abstractmethod
    def on_bar(self, bar):
        """
        on_bar触发
        :param bar:
        """
        pass

    @abc.abstractmethod
    def on_tick(self, tick):
        """
        on_tick触发
        :param tick:
        """
        pass

    @abc.abstractmethod
    def on_future_order(self, order):
        """
        委托回报
        :param order:
        """
        pass

    @abc.abstractmethod
    def on_future_order_canceled(self, order):
        """
        撤单成功回报
        :param order:
        """
        pass

    @abc.abstractmethod
    def on_future_cancel_order_failed(self, order_guid, msg):
        """
        撤单失败回报
        :param order_guid:
        :param msg:
        """
        pass

    @abc.abstractmethod
    def on_future_order_rejected(self, order):
        """
        委托拒绝回报
        :param order:
        """
        pass

    @abc.abstractmethod
    def on_future_trade(self, trade):
        """
        成交回报
        :param trade:
        """
        pass

    @abc.abstractmethod
    def on_exit(self):
        """
        当日结束
        """
        pass

    @abc.abstractmethod
    def on_end(self):
        """
        回测结束
        """
        pass

    def get_bar_series_by_date_time(self, market, instrument_id, interval, bar_type, begin_time):
        """
        根据时间获取K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param begin_time:
        :return:
        """
        return self.function.get_bar_series_by_date_time(market, instrument_id, interval, bar_type, begin_time)

    def get_bar_series_by_length(self, market: object, instrument_id: object, interval: object, bar_type: object, max_length: object) -> object:
        """
        根据回溯根数获取K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param max_length:
        :return:
        """
        return self.function.get_bar_series_by_length(market, instrument_id, interval, bar_type, max_length)

    def save_strategy(self, excel_record_path, fig_record_path):
        """
        保存策略相关回测信息
        """
        try:
            dic_data = {
                'Asset': self.function.df_asset,
                'Order': self.function.df_order,
                'Trade': self.function.df_trade,
                'Position': self.function.df_position,
                'PositionDetail': self.function.df_position_detail,
                'Summary': self.function.df_summary,
                'Param': self.function.df_param,
            }
            FileToolBox.save_excel(excel_record_path, **dic_data)
            self.function.df_asset['累计收益率(%)'] = self.function.df_asset['累计收益率'].str.strip('%').astype(float) / 100
            FileToolBox.save_fig(fig_record_path, self.function.df_asset, '日期', ['累计收益率(%)'])
        except Exception as e:
            print(str(e))

    def save_mongodb(self, db_name, collection_name, account_id):
        """
        保存记录到数据库
        @param db_name:
        @param collection_name:
        @param account_id:
        """
        try:
            record = {
                'version': 1.0,
                'drive_code': self.drive_code,
                'start_simulate_date': self.start_simulate_date,
                'end_simulate_date': self.end_simulate_date,
                'account_id': account_id,
                '_asset': self.function.df_asset.to_dict('records'),
                'trade': self.function.df_trade.to_dict('records'),
                'summary': self.function.df_summary.to_dict('records')[0],
                'param': self.function.df_param.set_index(['参数名']).T.to_dict('records')[0],
                'update_time': datetime.datetime.now(),
                'run_seconds': self.function.run_seconds
            }
            db = self.mongodb_client[db_name]
            collection = db[collection_name]
            collection.insert_one(record)
        except Exception as e:
            print(str(e))
            print('保存数据库出错，自动转存文件格式保存......')
            excel_record_path = os.path.join(self.record_dir, '{0}.xlsx'.format(account_id))
            fig_record_path = os.path.join(self.record_dir, '{0}.png'.format(account_id))
            self.save_strategy(excel_record_path, fig_record_path)

    def get_future_position(self, instrument_id, direction):
        """
        获取期货持仓
        :param instrument_id:
        :param direction:
        :return:
        """
        return self.function.get_future_position('', self.product_code, self.strategy_id, instrument_id, direction)
