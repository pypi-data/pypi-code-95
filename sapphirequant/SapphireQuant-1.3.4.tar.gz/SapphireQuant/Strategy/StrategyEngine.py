import datetime
import os

import numpy as np
import pandas as pd

from SapphireQuant.DataStorage.Cache.FutureCache import EnumLiquidationType
from SapphireQuant.Lib.FileToolBox import FileToolBox

from SapphireQuant.Config.TradingDay import TradingDayHelper
from SapphireQuant.Core.Enum import EnumOpenClose, EnumPositionDirection, EnumBuySell, EnumMarket
from SapphireQuant.Core.Futures import FutureTrade
from SapphireQuant.Strategy.BaseStrategy import BaseStrategy


class StrategyEngine:
    """
    策略引擎
    """
    @staticmethod
    def simulate_by_trade(**kwargs):
        """
        利用Trade记录进行复盘
        :param kwargs:
                record_dir:输出记录的目录
                df_trade:[ProductCode, StrategyId, InstrumentId, Direction, OpenClose, Price, Volume, TradeTime, TradingDate, AccountId]
                # df_position:[ProductCode, StrategyId, InstrumentId, Direction, Volume, TradingDate, AccountId]
        :return:
        """
        df_trade = kwargs['df_trade']
        record_dir = kwargs['record_dir']
        df_trade['TradeTime'] = pd.to_datetime(df_trade['TradeTime'])
        df_trade['TradingDate'] = pd.to_datetime(df_trade['TradingDate'])
        df_all_asset = None
        df_all_summary = None
        for product_code, df_product_trade in df_trade.groupby(['ProductCode']):
            df_product_asset = None
            df_product_summary = None
            for strategy_id, df_strategy_trade in df_product_trade.groupby(['StrategyId']):
                begin_date = df_strategy_trade['TradingDate'].min()
                end_date = df_strategy_trade['TradingDate'].max()
                kwargs['drive_code'] = ''
                kwargs['subscribe_futures'] = ''
                kwargs['drive_bar_interval'] = None
                kwargs['drive_bar_type'] = None
                kwargs['start_simulate_date'] = begin_date
                kwargs['end_simulate_date'] = end_date
                kwargs['product_code'] = product_code
                kwargs['strategy_id'] = strategy_id
                kwargs['liquidation_type'] = EnumLiquidationType.收盘价
                strategy = BaseStrategy(**kwargs)
                print('{0}-{1}:{2}-{3}'.format(product_code, strategy_id, begin_date, end_date))
                lst_trading_days = TradingDayHelper.get_trading_days(begin_date, end_date)
                for trading_day in lst_trading_days:
                    strategy.day_begin(trading_day, trading_day)
                    df_today_trade = df_strategy_trade[df_strategy_trade['TradingDate'] == trading_day]
                    if len(df_today_trade) > 0:
                        df_today_trade = df_today_trade.sort_values(by="TradeTime", ascending=True).copy()
                        for index, row in df_today_trade.iterrows():
                            trade = FutureTrade()
                            trade.product_code = row['ProductCode']
                            trade.strategy_id = row['StrategyId']
                            trade.account_id = row['AccountId']
                            trade.instrument_id = row['InstrumentId']
                            trade.direction = row['Direction']
                            trade.open_close = row['OpenClose']
                            trade.trade_volume = row['Volume']
                            trade.trade_price = row['Price']
                            trade.trading_date = row['TradingDate']
                            trade.trade_time = row['TradeTime']
                            print('成交:{0}'.format(trade.to_string()))
                            strategy.future_cache.on_trade(trade)
                    for position in strategy.future_cache.get_future_positions():
                        # 主力合约不处理交割问题
                        if '9999' in position.instrument_id:
                            continue
                        if position.volume > 0:
                            if 'IC' in position.instrument_id or 'IF' in position.instrument_id or 'IH' in position.instrument_id:
                                year = int(position.instrument_id[2:4]) + 2000
                                month = int(position.instrument_id[4:6])
                                month_first_day = datetime.datetime(year, month, 1)
                                week_day = month_first_day.weekday()
                                if week_day <= 4:
                                    expire_date = month_first_day + datetime.timedelta(days=2 * 7 + 4 - week_day)
                                else:
                                    expire_date = month_first_day + datetime.timedelta(days=2 * 7 + 6 - week_day + 5)
                                expire_date = TradingDayHelper.get_first_trading_day(expire_date)
                            else:
                                future_info = kwargs['instrument_manager'][position.instrument_id]
                                expire_date = future_info.expire_date

                            if expire_date == trading_day:
                                print('到了交割日，还未交割，自动执行交割{0}'.format(expire_date))
                                trade = FutureTrade()
                                trade.product_code = position.product_code
                                trade.strategy_id = position.strategy_id
                                trade.account_id = position.account_id
                                trade.instrument_id = position.instrument_id
                                trade.trade_volume = position.volume
                                trade.trading_date = position.trading_date
                                trade.trade_time = position.trading_date + datetime.timedelta(hours=15)
                                trade.open_close = EnumOpenClose.平仓
                                if position.direction == EnumPositionDirection.多头:
                                    trade.direction = EnumBuySell.卖出
                                else:
                                    trade.direction = EnumBuySell.买入

                                day_bar_series = kwargs['data_handler'].load_day_bar_series(EnumMarket.期货, position.instrument_id, position.trading_date)
                                trade.trade_price = day_bar_series[0].平仓
                                print('交割单:{0}'.format(trade.to_string()))
                                strategy.future_cache.on_trade(trade)
                    strategy.day_end()
                strategy.generate_strategy_report()
                strategy.save_strategy(os.path.join(record_dir, '{0}.xlsx'.format(product_code)), os.path.join(record_dir, '{0}.png'.format(product_code)))
                df_temp = strategy.df_asset[['日期', '累计盈亏']]
                df_temp.rename(columns={'累计盈亏': '{0}_{1}'.format(product_code, strategy_id)}, inplace=True)
                if df_product_asset is None:
                    df_product_asset = df_temp
                else:
                    df_product_asset = df_product_asset.merge(df_temp, how='outer', on=['日期'])
                if df_product_summary is None:
                    df_product_summary = strategy.df_summary
                else:
                    df_product_summary = df_product_summary.append(strategy.df_summary, ignore_index=True)

            record_path = '{0}/{1}/产品记录明细.xlsx'.format(record_dir, product_code)
            if df_product_asset is None:
                continue
            df_product_asset = df_product_asset.replace(np.nan, 0)
            df_product_asset_diff = df_product_asset.diff()
            df_product_asset_diff = df_product_asset_diff.replace(np.nan, 0)
            df_product_asset_diff['日期'] = df_product_asset['日期']

            dic_product = {
                'Asset': df_product_asset,
                'Asset_In_Day': df_product_asset_diff,
                'Summary': df_product_summary
            }

            FileToolBox.save_excel(record_path, **dic_product)

            if df_all_asset is None:
                df_all_asset = df_product_asset
            else:
                df_all_asset = df_all_asset.merge(df_product_asset, how='outer', on=['日期'])
            if df_all_summary is None:
                df_all_summary = df_product_summary
            else:
                df_all_summary = df_all_summary.append(df_product_summary, ignore_index=True)

        record_path = '{0}/账号记录明细.xlsx'.format(record_dir)
        if df_all_asset is None:
            return
        df_all_asset = df_all_asset.replace(np.nan, 0)
        df_all_asset_diff = df_all_asset.diff()
        df_all_asset_diff['日期'] = df_all_asset['日期']
        df_all_asset_diff = df_all_asset_diff.replace(np.nan, 0)

        dic_all = {
            'Asset': df_all_asset,
            'Asset_In_Day': df_all_asset_diff,
            'Summary': df_all_summary
        }

        FileToolBox.save_excel(record_path, **dic_all)
