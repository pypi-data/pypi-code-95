import datetime

from SapphireQuant.Config.TradingDay import TradingDayHelper
from SapphireQuant.Core import QiLogger
from SapphireQuant.Core.Enum import EnumMarket, EnumBarType
from SapphireQuant.DataProcessing.BaseBarHelper import BaseBarHelper
from SapphireQuant.DataProcessing.QiDataController import QiDataController
from SapphireQuant.DataProcessing.QiDataDirectory import QiDataDirectory


class DataCheck:
    """
    数据检查
    """

    @staticmethod
    def check_bar_series(data_handler, instrument_ids, exchange_id, begin_date, end_date, log_dir=None):
        """
        检查K线
        :param data_handler:
        :param end_date:
        :param begin_date:
        :param log_dir:
        :param instrument_ids:
        :param exchange_id:
        """
        log = None
        if log_dir is not None:
            log = QiLogger.create_log(log_dir, '{0}.log'.format(exchange_id))
        if log is not None:
            log.info('开始检查:{0}个品种,[{1}-{2}]:{3}'.format(len(instrument_ids), begin_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'), instrument_ids))
        for instrument_id in instrument_ids:
            listing_date = data_handler.instrument_manager.get_listing_date(EnumMarket.期货, instrument_id)
            if listing_date > begin_date:
                begin_date = listing_date
                if log is not None:
                    log.info('[{0}][{1}]:begin_date切换：{2}'.format(exchange_id, instrument_id, begin_date))
            if log is not None:
                log.info('开始检查:{0},[{1}-{2}]'.format(instrument_id, begin_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')))
            lst_trading_days = TradingDayHelper.get_trading_days(begin_date, end_date)
            for trading_date in lst_trading_days:
                print('开始检查:{0},[{1}]'.format(instrument_id, trading_date.strftime('%Y%m%d')))
                df_bar_series = data_handler.load_min_bar_data_frame(EnumMarket.期货, instrument_id, trading_date)
                df_bar_series_standard = BaseBarHelper.load_data_frame_in_day_date_time_slice_by_date(data_handler.instrument_manager,
                                                                                                      instrument_id, trading_date, trading_date, 1, EnumBarType.minute)
                if (df_bar_series is None) or len(df_bar_series) == 0:
                    if log is not None:
                        log.error('[{0}][{1}][{2}]:缺少数据'.format(exchange_id, instrument_id, trading_date))
                else:
                    last_bar_end_time = df_bar_series.loc[len(df_bar_series) - 1, 'end_time']
                    last_bar_end_time_delta = datetime.timedelta(hours=last_bar_end_time.hour, minutes=last_bar_end_time.minute,
                                                                 seconds=last_bar_end_time.second, microseconds=last_bar_end_time.microsecond)
                    if datetime.timedelta(hours=14, minutes=59, seconds=1) < last_bar_end_time_delta < datetime.timedelta(hours=15, minutes=0, seconds=59):
                        df_bar_series.loc[len(df_bar_series) - 1, 'end_time'] = datetime.datetime(last_bar_end_time.year, last_bar_end_time.month, last_bar_end_time.day, 15, 0, 0)
                    if datetime.timedelta(hours=15, minutes=14, seconds=1) < last_bar_end_time_delta < datetime.timedelta(hours=15, minutes=15, seconds=59):
                        df_bar_series.loc[len(df_bar_series) - 1, 'end_time'] = datetime.datetime(last_bar_end_time.year, last_bar_end_time.month, last_bar_end_time.day, 15, 15, 0)

                    df_combine = df_bar_series.merge(df_bar_series_standard, on=['begin_time', 'end_time'], how='outer')
                    nan_rows = df_combine[df_combine.isnull().T.any().T]
                    if len(nan_rows) > 0:
                        if log is not None:
                            log.error('[{0}][{1}][{2}]:缺少数据'.format(exchange_id, instrument_id, trading_date))
                            log.info(nan_rows)
            print('[{0}][{1}]:检查完毕，共计检查{2}个交易日'.format(exchange_id, instrument_id, len(lst_trading_days)))

    @staticmethod
    def check_bar_series_by_exchange(data_handler, exchange_id, begin_date, end_date, log_dir=None):
        """
        按市场检查K线，检查市场内所有品种
        :param data_handler:
        :param exchange_id:
        :param begin_date:
        :param end_date:
        :param log_dir:
        """
        product_ids = data_handler.instrument_manager.get_product_ids(EnumMarket.期货, exchange_id)
        lst_instrument_id = []
        for product_id in product_ids:
            lst_instrument_id.append('{0}9999'.format(product_id))
        DataCheck.check_bar_series(data_handler, lst_instrument_id, exchange_id, begin_date, end_date, log_dir)


if __name__ == '__main__':
    server_ip = '192.168.1.200'

    qi_data_directory = QiDataDirectory()
    qi_data_directory.future_tick = "\\\\{0}\\MqData\\futuretick\\Future".format(server_ip)
    qi_data_directory.future_tick_cache = "\\\\{0}\\MqData\\futuretick\\Future".format(server_ip)
    qi_data_directory.future_min = "\\\\{0}\\MqData\\futuremin".format(server_ip)
    qi_data_directory.future_day = "\\\\{0}\\MqData\\futureday".format(server_ip)
    qi_data_directory.trading_day = datetime.datetime(3020, 1, 1)
    data_handler = QiDataController(qi_data_directory)

    log_dir = 'D:\\DataCheck\\{0}'.format(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
    begin_date = datetime.datetime(2018, 1, 1)
    end_date = datetime.datetime(2020, 5, 10)


    # begin_date = datetime.datetime(2015, 12, 17)
    # end_date = datetime.datetime(2015, 12, 17)
    # DataCheck.check_bar_series(data_handler, ['IH9999'], 'CFFEX', begin_date, end_date, log_dir)

    DataCheck.check_bar_series_by_exchange(data_handler, 'CFFEX', begin_date, end_date, log_dir)
    DataCheck.check_bar_series_by_exchange(data_handler, 'SHFE', begin_date, end_date, log_dir)
    DataCheck.check_bar_series_by_exchange(data_handler, 'DCE', begin_date, end_date, log_dir)
    DataCheck.check_bar_series_by_exchange(data_handler, 'CZCE', begin_date, end_date, log_dir)
    DataCheck.check_bar_series_by_exchange(data_handler, 'INE', begin_date, end_date, log_dir)

    # p = Pool(10)
    # p.apply_async(data_checker.check_bar_series, args=[['MA9999'], 'CZCE', datetime.datetime(2019, 1, 1), datetime.datetime.today()])
    # p.apply_async(check, args=[instrument_ids_CFFEX, 'CFFEX'])
    # p.apply_async(check, args=[instrument_ids_SHFE, 'SHFE'])
    # p.apply_async(check, args=[instrument_ids_DCE, 'DCE'])
    # p.apply_async(check, args=[instrument_ids_CZCE, 'CZCE'])
    # p.apply_async(check, args=[instrument_ids_INE, 'INE'])
    # p.close()
    # p.join()
