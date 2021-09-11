# -*- coding: utf-8 -*-
import wencai as wc
from wencai.core.crawler import Wencai
wc.set_variable(cn_col=True, proxies=[{'http': 'http://localhost:1087', 'https': 'http://localhost:1087'},{'http': 'http://localhost:1087', 'https': 'http://localhost:1087'}])

r = wc.search('当前热股')
print(r)

# r = wc.get_strategy(query='当前热股',
# start_date='2018-10-09',
# end_date='2019-07-16',
# period='1',
# fall_income=1,
# lower_income=5,
# upper_income=9,
# day_buy_stock_num=1,
# stock_hold=2)
# print(r.profit_data) # 累计收益数据
# print(r.backtest_data) # 报告评级
# print(r.condition_data) # 准确回测语句
# print(r.history_detail(period='1')) # 历史明细查询
# print(r.history_pick(trade_date='2019-07-16', hold_num=10))

# exit()
#
# r = wc.get_scrape_report(query='非停牌；非st；今日振幅小于5%；量比小于1；涨跌幅大于-5%小于1%；流通市值小于20亿；市盈率大于25小于80；主力控盘比例从大到小',
#                      start_date='2021-01-10',
#                      end_date='2021-01-20',
#                      period='1,2,3,4',
#                      benchmark='hs000300')
# print(r.history_detail(period='2'))
#
# exit()

# r = wc.get_strategy(query='非停牌；非st；今日振幅小于5%；量比小于1；涨跌幅大于-5%小于1%；流通市值小于20亿；市盈率大于25小于80；主力控盘比例从大到小',
#                     start_date='2018-10-09',
#                     end_date='2019-07-16',
#                     period='1',
#                     fall_income=1,
#                     lower_income=5,
#                     upper_income=9,
#                     day_buy_stock_num=1,
#                     stock_hold=2)
# print(r.profit_data)
# print(r.backtest_data)
# print(r.condition_data)
# print(r.history_detail(period='1'))
# print(r.history_pick(trade_date='2019-07-16', hold_num=1))

# r = wc.get_strategy(query='非停牌；非st；今日振幅小于5%；量比小于1；涨跌幅大于-5%小于1%；流通市值小于20亿；市盈率大于25小于80；主力控盘比例从大到小',
#                     start_date='2018-10-09',
#                     end_date='2019-07-16',
#                     period='1',
#                     fall_income=1,
#                     lower_income=5,
#                     upper_income=9,
#                     day_buy_stock_num=1,
#                     stock_hold=2)
# print(r.profit_data)
# print(r.backtest_data)
# print(r.condition_data)
# print(r.history_detail(period='1'))
# print(r.history_pick(trade_date='2019-07-16', hold_num=1))