def test_send_order_limit_price(trade_channel, instrument_id, exchange_id, direction, open_close, price, volume):
    """
    测试限价发单
    :param trade_channel:
    :param instrument_id:
    :param exchange_id:
    :param direction:
    :param open_close:
    :param price:
    :param volume:
    """
    if trade_channel.broker_id != '9999':
        print('非SimNow账户不允许测试发单......')
        return None
    return trade_channel.send_order_limit_price(instrument_id, exchange_id, direction, open_close, price, volume)


def test_send_order_any_price(trade_channel, instrument_id, exchange_id, direction, open_close, volume):
    """
    测试市价发单
    :param trade_channel:
    :param instrument_id:
    :param exchange_id:
    :param direction:
    :param open_close:
    :param volume:
    """
    if trade_channel.broker_id != '9999':
        print('非SimNow账户不允许测试发单......')
        return None
    return trade_channel.send_order_any_price(instrument_id, exchange_id, direction, open_close, volume)


def test_cancel_order(trade_channel, order):
    """
    测试撤单
    :param trade_channel:
    :param order:
    """
    trade_channel.cancel_order(order)


def test_query_instrument(trade_channel, instrument_id=None):
    """
    测试查询合约
    :param trade_channel:
    :param instrument_id:
    """
    lst_future_info = trade_channel.query_instrument(instrument_id=instrument_id)
    for future_info in lst_future_info:
        print(future_info.to_string())


def test_query_asset(trade_channel):
    """
    测试查询账户资金
    :param trade_channel:
    """
    asset = trade_channel.query_asset()
    print(asset.to_string())


def test_query_orders(trade_channel):
    """
    测试查询委托
    :param trade_channel:
    """
    lst_data = trade_channel.query_orders()
    for data in lst_data:
        print(data.to_string())


def test_query_trades(trade_channel):
    """
    测试查询交易
    :param trade_channel:
    """
    lst_data = trade_channel.query_trades()
    for data in lst_data:
        print(data.to_string())


def test_query_positions(trade_channel):
    """
    测试查询持仓
    :param trade_channel:
    """
    lst_data = trade_channel.query_positions()
    for data in lst_data:
        print(data.to_string())


def test_query_position_details(trade_channel):
    """
    测试查询持仓明细
    :param trade_channel:
    """
    lst_data = trade_channel.query_position_details()
    lst_data.sort(key=lambda x: x.open_time, reverse=True)
    for data in lst_data:
        print(data.to_string())


def test_query_settlement_info(trade_channel, trading_date):
    """
    测试查询结算单
    :param trading_date:
    :param trade_channel:
    """
    settlement_info = trade_channel.query_settlement_info(trading_date)
    print(settlement_info)


def test_query_asset_by_trading_date(trade_channel, trading_date):
    """
    测试查询账户信息
    :param trade_channel:
    :param trading_date:
    """
    asset = trade_channel.query_asset_by_trading_date(trading_date)
    print(asset.to_string())
