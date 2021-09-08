import math

import numpy as np
import pandas as pd
from SapphireQuant.Config.TradingDay import TradingDayHelper


class StrategyToolBox:
    """
    策略工具箱
    """

    @staticmethod
    def calc_total_and_annual_yield_rate(df_asset, capital, trading_day_per_year, trading_day_num):
        """
        计算总收益率和年华收益率
        :param df_asset:
        :param capital:
        :param trading_day_per_year:
        :param trading_day_num:
        :return:
        """
        yield_rate = df_asset['净利润'].sum() / capital
        if yield_rate < 0:
            annual_yield_rate = -(math.pow(1 + abs(yield_rate), trading_day_per_year / trading_day_num) - 1)
        else:
            annual_yield_rate = math.pow(1 + abs(yield_rate), trading_day_per_year / trading_day_num) - 1

        return yield_rate, annual_yield_rate

    @staticmethod
    def calc_profit_per_hand(df_asset, total_trade_lots):
        """
        计算每手盈利
        :param df_asset:
        :param total_trade_lots:
        :return:
        """
        total_profit = df_asset['净利润'].sum()

        if total_trade_lots != 0:
            profit_per_hand = int(total_profit / total_trade_lots)
        else:
            profit_per_hand = 0
        return profit_per_hand

    @staticmethod
    def calc_max_retrace_rate(df_asset, capital):
        """
        计算最大回撤
        :param df_asset:
        :param capital:
        :return:
        """
        cum_trade_df = df_asset[['净利润']].cumsum(axis=0)
        tp = round(cum_trade_df.loc[len(cum_trade_df) - 1, '净利润'], 0)
        max_retracement = 0
        high_level = 0

        if tp >= 0:
            for v in range(len(cum_trade_df)):
                if cum_trade_df.loc[v, '净利润'] > high_level:
                    high_level = cum_trade_df.loc[v, '净利润']
                temp = cum_trade_df.loc[v, '净利润'] - high_level
                if temp < max_retracement:
                    max_retracement = temp
        elif tp < 0:
            for v in range(len(cum_trade_df)):
                if cum_trade_df.loc[v, '净利润'] < high_level:
                    high_level = cum_trade_df.loc[v, '净利润']
                temp = cum_trade_df.loc[v, '净利润'] - high_level
                if temp > max_retracement:
                    max_retracement = temp

        max_retrace_rate = max_retracement / capital
        return max_retrace_rate

    @staticmethod
    def calc_current_max_retrace_rate(df_asset, capital):
        """
        计算当前最大回撤
        :param df_asset:
        :param capital:
        :return:
        """
        cum_trade_df = df_asset[['净利润']].cumsum(axis=0)
        tp = round(cum_trade_df.loc[len(cum_trade_df) - 1, '净利润'], 0)
        current_retracement = 0
        high_level = 0

        if tp >= 0:
            for v in range(len(cum_trade_df)):
                if cum_trade_df.loc[v, '净利润'] > high_level:
                    high_level = cum_trade_df.loc[v, '净利润']
                temp = cum_trade_df.loc[v, '净利润'] - high_level
                if temp < 0:
                    current_retracement = temp
                else:
                    current_retracement = 0
        elif tp < 0:
            for v in range(len(cum_trade_df)):
                if cum_trade_df.loc[v, '净利润'] < high_level:
                    high_level = cum_trade_df.loc[v, '净利润']
                temp = cum_trade_df.loc[v, '净利润'] - high_level
                if temp > 0:
                    current_retracement = temp
                else:
                    current_retracement = 0

        current_retrace_rate = current_retracement / capital
        return current_retrace_rate

    @staticmethod
    def calc_retrace_ratio(max_retrace_rate, annual_yield_rate):
        """
        计算收益回撤比
        :param max_retrace_rate:
        :param annual_yield_rate:
        :return:
        """
        if max_retrace_rate != 0:
            retrace_ratio = round(
                abs(annual_yield_rate / max_retrace_rate), 2)
        else:
            retrace_ratio = np.nan
        return retrace_ratio

    @staticmethod
    def calc_sharpe_ratio(df_asset, capital):
        """
        计算夏普率
        :param df_asset:
        :param capital:
        :return:
        """
        try:
            return_per_day = df_asset['净利润'] / capital
            sharpe_ratio = return_per_day.mean() / return_per_day.std() * np.sqrt(252)
            return sharpe_ratio
        except Exception as e:
            print('计算夏普率出错:{0}'.format(str(e)))
            return 0

    @staticmethod
    def calc_max_continuous_no_innovation_high_days(df_asset):
        """
        计算最大连续不创新高天数
        @param df_asset:
        """
        high = 0
        days = 0
        max_days = 0
        for index, row in df_asset.iterrows():
            value = row['累计盈亏']
            if value >= high:
                high = value
                if days > max_days:
                    max_days = days
                days = 0
            else:
                days += 1

        if days > max_days:
            max_days = days
        return max_days

    @staticmethod
    def calc_current_max_continuous_no_innovation_high_days(df_asset):
        """
        计算当前最大连续不创新高天数
        @param df_asset:
        """
        high = 0
        days = 0
        for index, row in df_asset.iterrows():
            value = row['累计盈亏']
            if value >= high:
                high = value
                days = 0
            else:
                days += 1
        return days

    @staticmethod
    def calc_max_loss_days(df_asset):
        """
        计算最大连续亏损天数
        @param df_asset:
        """
        days = 0
        max_days = 0
        for index, row in df_asset.iterrows():
            value = row['净利润']
            if value >= 0:
                if days > max_days:
                    max_days = days
                days = 0
            else:
                days += 1

        if days > max_days:
            max_days = days
        return max_days

    @staticmethod
    def compare_trade(df_source, df_target, how='outer', begin_date=None, end_date=None, source_suffix=None, target_suffix=None):
        """
        对比成交
        :param how:
        :param target_suffix:
        :param source_suffix:
        :param df_source:必须包含列名：['交易日', '价格', '合约', '多空', '开平', '时间', '量']
        :param df_target:必须包含列名：['交易日', '价格', '合约', '多空', '开平', '时间', '量']
        :param begin_date:
        :param end_date:
        """

        df_source = df_source[['交易日', '价格', '合约', '多空', '开平', '时间', '量']]
        df_source['时分'] = df_source['时间'].apply(lambda x: x.strftime('%H:%M'))
        df_source['时间'] = df_source['时间'].apply(lambda x: x.strftime('%H:%M:%S'))
        df_source.loc[df_source['开平'] == '平今仓', '开平'] = '平仓'
        if begin_date is not None:
            df_source = df_source[df_source['交易日'] >= begin_date].copy()
        if end_date is not None:
            df_source = df_source[df_source['交易日'] <= end_date].copy()
        if source_suffix is not None:
            df_source.rename(columns={'时间': '时间_{0}'.format(source_suffix), '价格': '价格_{0}'.format(source_suffix), '量': '量_{0}'.format(source_suffix)}, inplace=True)
        else:
            df_source.rename(columns={'时间': '时间_1', '价格': '价格_1', '量': '量_1'}, inplace=True)

        df_target['时分'] = df_target['时间'].apply(lambda x: x.strftime('%H:%M'))
        df_target['时间'] = df_target['时间'].apply(lambda x: x.strftime('%H:%M:%S'))
        df_target.loc[df_target['开平'] == '平今仓', '开平'] = '平仓'
        if begin_date is not None:
            df_target = df_target[df_target['交易日'] >= begin_date].copy()
        if end_date is not None:
            df_target = df_target[df_target['交易日'] <= end_date].copy()
        if source_suffix is not None:
            df_target.rename(columns={'时间': '时间_{0}'.format(target_suffix), '价格': '价格_{0}'.format(target_suffix), '量': '量_{0}'.format(target_suffix)}, inplace=True)
        else:
            df_target.rename(columns={'时间': '时间_2', '价格': '价格_2', '量': '量_2'}, inplace=True)
        df_all = df_source.merge(df_target, on=['交易日', '时分', '合约', '多空', '开平'], how=how)
        df_all = df_all.sort_values(by=['交易日', '时分'], axis=0, ascending=True)
        df_all.reset_index(inplace=True)
        return df_all

    @staticmethod
    def combine_asset(lst_df_data):
        """
        组合Asset
        @param lst_df_data:
        """
        df_combine = None
        for df_asset in lst_df_data:
            if df_combine is None:
                df_combine = df_asset
            else:
                df_combine = df_combine.merge(df_asset, on=['日期'], how='outer')
                df_combine['昨日结存'] = df_combine['昨日结存_x'] + df_combine['昨日结存_y']
                df_combine['动态权益'] = df_combine['动态权益_x'] + df_combine['动态权益_y']
                df_combine['平仓盈亏'] = df_combine['平仓盈亏_x'] + df_combine['平仓盈亏_y']
                df_combine['持仓盈亏'] = df_combine['持仓盈亏_x'] + df_combine['持仓盈亏_y']
                df_combine['净利润'] = df_combine['净利润_x'] + df_combine['净利润_y']
                df_combine['可用资金'] = df_combine['可用资金_x'] + df_combine['可用资金_y']
                df_combine['持仓保证金'] = df_combine['持仓保证金_x'] + df_combine['持仓保证金_y']
                df_combine['手续费'] = df_combine['手续费_x'] + df_combine['手续费_y']
                df_combine = df_combine[['日期', '昨日结存', '动态权益', '平仓盈亏', '持仓盈亏', '净利润', '手续费', '可用资金', '持仓保证金']]
        df_combine['累计盈亏'] = df_combine[['净利润']].cumsum(axis=0)
        df_combine['累计收益率'] = df_combine['累计盈亏'] / df_combine['昨日结存'][0]
        df_combine['累计收益率'] = df_combine['累计收益率'].apply(lambda x: format(x, '.2%'))
        return df_combine

    @staticmethod
    def combine_trade(lst_df_data):
        """
        组合Asset
        @param lst_df_data:
        """
        df_combine = None
        for df_trade in lst_df_data:
            if df_combine is None:
                df_combine = df_trade
            else:
                df_combine = df_combine.concat(df_trade)
        df_combine.sort_values(by=['交易日', '时间'], ascending=True, inplace=True)
        return df_combine

    @staticmethod
    def get_strategy_param(df_param):
        """
        获取策略的参数
        @param df_param:
        @return:
        """
        dic_param = {}
        for index, row in df_param.iterrows():
            dic_param[row['参数名']] = row['参数值']
        return dic_param

    @staticmethod
    def get_strategy_summary(df_asset, df_trade, begin_date, end_date):
        """
        获取策略报告
        :param df_asset:
        :param df_trade:
        :param begin_date:
        :param end_date:
        """
        fund_balance = df_asset.iloc['昨日结存'][0]
        df_asset = df_asset[df_asset['交易日'] >= begin_date]
        df_asset = df_asset[df_asset['交易日'] <= end_date]
        df_trade = df_trade[df_trade['交易日'] >= begin_date]
        df_trade = df_trade[df_trade['交易日'] <= end_date]
        trading_day_num = TradingDayHelper.get_trading_day_count(begin_date, end_date)
        total_trade_lots = df_trade['量'].sum() / 2
        volume_per_day = total_trade_lots / len(df_asset)
        yield_rate = StrategyToolBox.calc_total_and_annual_yield_rate(df_asset, fund_balance, 243, trading_day_num)
        total_yield_rate = yield_rate[0]
        annual_yield_rate = yield_rate[1]
        profit_per_hand = StrategyToolBox.calc_profit_per_hand(df_asset, total_trade_lots)
        max_retrace_rate = StrategyToolBox.calc_max_retrace_rate(df_asset, fund_balance)
        retrace_ratio = StrategyToolBox.calc_retrace_ratio(max_retrace_rate, annual_yield_rate)
        sharpe_ratio = StrategyToolBox.calc_sharpe_ratio(df_asset, fund_balance)
        lst_summary = [
            [begin_date, end_date, trading_day_num, total_trade_lots, volume_per_day,
             total_yield_rate, annual_yield_rate, profit_per_hand, max_retrace_rate, retrace_ratio, sharpe_ratio]]
        df_summary = pd.DataFrame(lst_summary, columns=['开始日期', '截止日期', '交易天数', '总手数', '日均手数',
                                                        '总收益', '年化收益', '每手盈利', '最大回撤', '收益回撤比', '夏普率'])
        return df_summary
