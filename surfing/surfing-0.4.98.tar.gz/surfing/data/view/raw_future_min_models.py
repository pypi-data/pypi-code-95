
import datetime
from os import close
from typing import MutableMapping, MutableSet
from sqlalchemy import CHAR, Column, Integer, TEXT, BOOLEAN, text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, TINYINT, DATETIME, MEDIUMTEXT, YEAR, SMALLINT, BIGINT, DECIMAL, VARCHAR
from sqlalchemy.orm.session import make_transient_to_detached


class Base():
    _update_time = Column('_update_time', DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间

# make this column at the end of every derived table
Base._update_time._creation_order = 9999
Base = declarative_base(cls=Base)


class FutureBasic(Base):
    '''期货基金信息表'''

    __tablename__ = 'future_basic'

    future_id = Column(CHAR(20), primary_key=True) # 期货代码
    underlying = Column(CHAR(40)) # 标的物
    mult = Column(DOUBLE(asdecimal=False)) # 合约乘数
    mult_unit = Column(CHAR(40)) # 合约乘数单位
    tick_size = Column(DOUBLE(asdecimal=False)) # 最小变动价位
    ret_down_limit = Column(DOUBLE(asdecimal=False)) # 每日价格最大波动下限%
    ret_up_limit = Column(DOUBLE(asdecimal=False)) # 每日价格最大波动上限%
    margin = Column(DOUBLE(asdecimal=False)) # 最低交易保证金%
    delivery_way = Column(CHAR(40)) # 交割方式
    market = Column(CHAR(64)) # 上市交易所
    future_class = Column(CHAR(40)) # 期货大类别
    future_type = Column(CHAR(64)) # 期货小类别
    end_date = Column(DATE) # 最后交易日
    endt_ref = Column(CHAR(64)) # 最后交易日参考标准
    endt_type = Column(CHAR(64)) # 最后交易日类别
    endt_diff = Column(DOUBLE(asdecimal=False)) # 最后交易日相对最后交易日所在月份偏移天数
    endt_isdelay = Column(CHAR(64)) # 最后交易日是否假日顺延
    delivery_endt = Column(DATE) # 最后交割日
    delivery_endt_ref = Column(CHAR(64)) # 最后交割日参照标准
    delivery_endt_type = Column(CHAR(64)) # 最后交割日类别
    delivery_endt_diff = Column(DOUBLE(asdecimal=False)) # 最后交割日相对最后交割日所在月份偏移天数
    delivery_endt_is_delay = Column(CHAR(16)) # 最后交割日是否假日顺延

class FutureMinute(Base):
    '''期货分钟数据'''

    __tablename__ = 'future_minute'

    future_id = Column(CHAR(20), primary_key=True) # 期货代码
    datetime = Column(DATETIME, primary_key=True) # 时间
    date = Column((DATE), primary_key=True) # 频率
    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    pre_bar_close = Column(DOUBLE(asdecimal=False)) # 前一时刻收盘价
    pre_day_close = Column(DOUBLE(asdecimal=False)) # 上一日收盘价
    volume = Column(DOUBLE(asdecimal=False)) # 成交量
    amount = Column(DOUBLE(asdecimal=False)) # 成交额
    ret = Column(DOUBLE(asdecimal=False)) # 收益率
    lnret = Column(DOUBLE(asdecimal=False)) # 对数收益率
    accum_sell_vol = Column(DOUBLE(asdecimal=False)) # 当前累计卖出成交量
    accum_buy_vol = Column(DOUBLE(asdecimal=False)) # 当前累计买入成交量
    accum_sell_amt = Column(DOUBLE(asdecimal=False)) # 当前累计卖出金额
    accum_buy_amt = Column(DOUBLE(asdecimal=False)) # 当前累计买入金额
    accum_submit_sell_vol = Column(DOUBLE(asdecimal=False)) # 当前累计委托卖量
    accum_submit_buy_vol = Column(DOUBLE(asdecimal=False)) # 当前累计委托买量
    accum_wb = Column(DOUBLE(asdecimal=False)) # 当前累计委托
