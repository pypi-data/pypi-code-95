import datetime


from SapphireQuant.Core import Tick, Quote

from SapphireQuant.Core.Futures import FutureOrder, FutureTrade, FuturePosition, FutureAsset, FuturePositionDetail

from SapphireQuant.Core.Enum import EnumBuySell, EnumPositionDirection, EnumOpenClose, EnumHedgeFlag, EnumOrderStatus, EnumOrderSubmitStatus, EnumMarket, EnumPositionType, EnumProductClass
from SapphireQuant.Core.Enum.EnumOrderPriceType import EnumOrderPriceType
from SapphireQuant.Core.Enum.EnumOrderRejectReason import EnumOrderRejectReason
from SapphireQuant.Core.Enum.EnumOrderType import EnumOrderType
from SapphireQuant.Channel.CtpChannel import thosttraderapi as api


class CtpConvert:
    """
    Ctp转换
    """
    @staticmethod
    def convert_product_class(ctp_product_class):
        """
        转换柜台的ProductClass
        :param ctp_product_class:
        """
        product_class = None
        if ctp_product_class == api.THOST_FTDC_PC_Futures:
            product_class = EnumProductClass.future
        elif ctp_product_class == api.THOST_FTDC_PC_Options:
            product_class = EnumProductClass.option
        elif ctp_product_class == api.THOST_FTDC_PC_Combination:
            product_class = EnumProductClass.combination
        elif ctp_product_class == api.THOST_FTDC_PC_Spot:
            product_class = EnumProductClass.spot
        elif ctp_product_class == api.THOST_FTDC_PC_EFP:
            product_class = EnumProductClass.efp
        elif ctp_product_class == api.THOST_FTDC_PC_SpotOption:
            product_class = EnumProductClass.spot_option
        return product_class

    @staticmethod
    def convert_tick(ctp_tick):
        """

        :param ctp_tick:
        """
        tick = Tick()
        tick.market = EnumMarket.期货
        tick.trading_date = datetime.datetime.strptime(ctp_tick.TradingDay, '%Y%m%d')
        tick.instrument_id = ctp_tick.InstrumentID
        tick.exchange_id = ctp_tick.ExchangeID
        #  ctp_tick.ExchangeInstID
        tick.last_price = ctp_tick.LastPrice
        tick.pre_settlement_price = ctp_tick.PreSettlementPrice
        tick.pre_close_price = ctp_tick.PreClosePrice
        tick.pre_open_interest = ctp_tick.PreOpenInterest
        tick.open_price = ctp_tick.OpenPrice
        tick.high_price = ctp_tick.HighestPrice
        tick.low_price = ctp_tick.LowestPrice
        tick.volume = ctp_tick.Volume
        tick.turnover = ctp_tick.Turnover
        tick.open_interest = ctp_tick.OpenInterest
        #  ctp_tick.ClosePrice,
        #  ctp_tick.SettlementPrice,
        tick.up_limit = ctp_tick.UpperLimitPrice
        tick.drop_limit = ctp_tick.LowerLimitPrice
        #  ctp_tick.PreDelta
        #  ctp_tick.CurrDlta
        tick.date_time = datetime.datetime.strptime('{0} {1}'.format(ctp_tick.TradingDay, ctp_tick.UpdateTime), '%Y%m%d %H:%M:%S')
        #  ctp_tick.UpdateMillisec
        tick.bid_price1 = ctp_tick.BidPrice1
        tick.bid_volume1 = ctp_tick.BidVolume1
        tick.ask_price1 = ctp_tick.AskPrice1
        tick.ask_volume1 = ctp_tick.AskVolume1
        tick.quote = Quote()
        tick.quote.bid_price1 = ctp_tick.BidPrice1
        tick.quote.bid_volume1 = ctp_tick.BidVolume1
        tick.quote.ask_price1 = ctp_tick.AskPrice1
        tick.quote.ask_volume1 = ctp_tick.AskVolume1

        tick.quote.bid_price2 = ctp_tick.BidPrice2
        tick.quote.bid_volume2 = ctp_tick.BidVolume2
        tick.quote.ask_price2 = ctp_tick.AskPrice2
        tick.quote.ask_volume2 = ctp_tick.AskVolume2

        tick.quote.bid_price3 = ctp_tick.BidPrice3
        tick.quote.bid_volume3 = ctp_tick.BidVolume3
        tick.quote.ask_price3 = ctp_tick.AskPrice3
        tick.quote.ask_volume3 = ctp_tick.AskVolume3

        tick.quote.bid_price4 = ctp_tick.BidPrice4
        tick.quote.bid_volume4 = ctp_tick.BidVolume4
        tick.quote.ask_price4 = ctp_tick.AskPrice4
        tick.quote.ask_volume4 = ctp_tick.AskVolume4

        tick.quote.bid_price5 = ctp_tick.BidPrice5
        tick.quote.bid_volume5 = ctp_tick.BidVolume5
        tick.quote.ask_price5 = ctp_tick.AskPrice5
        tick.quote.ask_volume5 = ctp_tick.AskVolume5
        #  ctp_tick.AveragePrice,
        #  ctp_tick.ActionDay,
        tick.date_time = tick.date_time + datetime.timedelta(milliseconds=int(ctp_tick.UpdateMillisec))
        tick.local_time = datetime.datetime.now()
        return tick

    @staticmethod
    def convert_direction(ctp_direction):
        """
        转换柜台的Direction
        :param ctp_direction:
        """
        direction = None
        if ctp_direction == api.THOST_FTDC_D_Buy:
            direction = EnumBuySell.买入
        elif ctp_direction == api.THOST_FTDC_D_Sell:
            direction = EnumBuySell.卖出
        return direction

    @staticmethod
    def convert_position_direction(ctp_position_direction):
        """
        转换柜台的Direction
        :param ctp_position_direction:
        """
        position_direction = None
        if ctp_position_direction == api.THOST_FTDC_PD_Long:
            position_direction = EnumPositionDirection.多头
        elif ctp_position_direction == api.THOST_FTDC_PD_Short:
            position_direction = EnumPositionDirection.空头
        elif ctp_position_direction == api.THOST_FTDC_PD_Net:
            position_direction = EnumPositionDirection.净持仓
        return position_direction

    @staticmethod
    def convert_open_close(ctp_open_close):
        """
        转换柜台的OpenClose
        :param ctp_open_close:
        """
        open_close = None
        if ctp_open_close == api.THOST_FTDC_OF_Open:
            open_close = EnumOpenClose.开仓
        elif ctp_open_close == api.THOST_FTDC_OF_Close:
            open_close = EnumOpenClose.平仓
        elif ctp_open_close == api.THOST_FTDC_OF_ForceClose:
            open_close = EnumOpenClose.强平
        elif ctp_open_close == api.THOST_FTDC_OF_CloseToday:
            open_close = EnumOpenClose.平今
        elif ctp_open_close == api.THOST_FTDC_OF_CloseYesterday:
            open_close = EnumOpenClose.平昨
        elif ctp_open_close == api.THOST_FTDC_OF_ForceOff:
            open_close = EnumOpenClose.强减
        elif ctp_open_close == api.THOST_FTDC_OF_LocalForceClose:
            open_close = EnumOpenClose.本地强平
        return open_close

    @staticmethod
    def convert_hedge_flag(ctp_hedge_flag):
        """
        转换柜台的OpenClose
        :param ctp_hedge_flag:
        """
        hedge_flag = None
        if ctp_hedge_flag == api.THOST_FTDC_BHF_Speculation:
            hedge_flag = EnumHedgeFlag.投机
        elif ctp_hedge_flag == api.THOST_FTDC_BHF_Arbitrage:
            hedge_flag = EnumHedgeFlag.套利
        elif ctp_hedge_flag == api.THOST_FTDC_BHF_Hedge:
            hedge_flag = EnumHedgeFlag.套保
        return hedge_flag

    @staticmethod
    def convert_order_type(ctp_order_type):
        """
        转换柜台的OpenClose
        :param ctp_order_type:
        """
        order_type = None
        if ctp_order_type == api.THOST_FTDC_ORDT_Normal:
            order_type = EnumOrderType.normal
        elif ctp_order_type == api.THOST_FTDC_ORDT_DeriveFromQuote:
            order_type = EnumOrderType.derive_from_quote
        elif ctp_order_type == api.THOST_FTDC_ORDT_DeriveFromCombination:
            order_type = EnumOrderType.derivce_from_combination
        elif ctp_order_type == api.THOST_FTDC_ORDT_Combination:
            order_type = EnumOrderType.combination
        elif ctp_order_type == api.THOST_FTDC_ORDT_ConditionalOrder:
            order_type = EnumOrderType.conditional_order
        elif ctp_order_type == api.THOST_FTDC_ORDT_Swap:
            order_type = EnumOrderType.swap
        elif ctp_order_type == api.THOST_FTDC_ORDT_DeriveFromBlockTrade:
            order_type = EnumOrderType.derive_from_block_trade
        elif ctp_order_type == api.THOST_FTDC_ORDT_DeriveFromEFPTrade:
            order_type = EnumOrderType.derive_from_EFP_trade
        return order_type

    @staticmethod
    def convert_order_reject_reason(error_msg):
        """
        转换柜台的OpenClose
        :param error_msg:
        """
        order_reject_reason = EnumOrderRejectReason.未知
        if "每秒请求超许可数" in error_msg:
            order_reject_reason = EnumOrderRejectReason.每秒请求超许可数
        if "价格非最小单位倍数" in error_msg:
            order_reject_reason = EnumOrderRejectReason.价格非最小单位倍数
        if "价格高于涨停板" in error_msg:
            order_reject_reason = EnumOrderRejectReason.价格高于涨停板
        if "价格低于跌停板" in error_msg:
            order_reject_reason = EnumOrderRejectReason.价格低于跌停板
        if "资金不足" in error_msg:
            order_reject_reason = EnumOrderRejectReason.资金不足
        if "平今仓位不足" in error_msg:
            order_reject_reason = EnumOrderRejectReason.平今仓位不足
        if "平昨仓位不足" in error_msg:
            order_reject_reason = EnumOrderRejectReason.平昨仓位不足
        if "不支持报单类型" in error_msg:
            order_reject_reason = EnumOrderRejectReason.不支持报单类型
        if "不支持套利类型报单" in error_msg:
            order_reject_reason = EnumOrderRejectReason.不支持套利类型报单
        if "保值额度不足" in error_msg:
            order_reject_reason = EnumOrderRejectReason.保值额度不足
        if "网络连接失败" in error_msg:
            order_reject_reason = EnumOrderRejectReason.网络连接失败
        if "Qi暂停开仓" in error_msg:
            order_reject_reason = EnumOrderRejectReason.Qi暂停开仓
        if "延迟开仓被Qi拒绝" in error_msg:
            order_reject_reason = EnumOrderRejectReason.延迟开仓被Qi拒绝
        if "报单数量错误" in error_msg:
            order_reject_reason = EnumOrderRejectReason.报单数量错误
        if "提交委托失败" in error_msg:
            order_reject_reason = EnumOrderRejectReason.提交委托失败
        return order_reject_reason

    @staticmethod
    def convert_order_price_type(ctp_order_price_type):
        """
        转换柜台的OrderPriceType
        :param ctp_order_price_type:
        """
        order_price_type = None
        if ctp_order_price_type == api.THOST_FTDC_OPT_AnyPrice:
            order_price_type = EnumOrderPriceType.市价
        elif ctp_order_price_type == api.THOST_FTDC_OPT_LimitPrice:
            order_price_type = EnumOrderPriceType.限价
        elif ctp_order_price_type == api.THOST_FTDC_OPT_BestPrice:
            order_price_type = EnumOrderPriceType.最优价
        elif ctp_order_price_type == api.THOST_FTDC_OPT_LastPrice:
            order_price_type = EnumOrderPriceType.最新价
        elif ctp_order_price_type == api.THOST_FTDC_OPT_LastPricePlusOneTicks:
            order_price_type = EnumOrderPriceType.最新价浮动上浮1个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_LastPricePlusTwoTicks:
            order_price_type = EnumOrderPriceType.最新价浮动上浮2个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_LastPricePlusThreeTicks:
            order_price_type = EnumOrderPriceType.最新价浮动上浮3个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_AskPrice1:
            order_price_type = EnumOrderPriceType.卖一价
        elif ctp_order_price_type == api.THOST_FTDC_OPT_AskPrice1PlusOneTicks:
            order_price_type = EnumOrderPriceType.卖一价浮动上浮1个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_AskPrice1PlusTwoTicks:
            order_price_type = EnumOrderPriceType.卖一价浮动上浮2个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_AskPrice1PlusThreeTicks:
            order_price_type = EnumOrderPriceType.卖一价浮动上浮3个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_BidPrice1:
            order_price_type = EnumOrderPriceType.买一价
        elif ctp_order_price_type == api.THOST_FTDC_OPT_BidPrice1PlusOneTicks:
            order_price_type = EnumOrderPriceType.买一价浮动上浮1个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_BidPrice1PlusTwoTicks:
            order_price_type = EnumOrderPriceType.买一价浮动上浮2个ticks
        elif ctp_order_price_type == api.THOST_FTDC_OPT_BidPrice1PlusThreeTicks:
            order_price_type = EnumOrderPriceType.买一价浮动上浮3个ticks
        return order_price_type

    @staticmethod
    def convert_order_status(ctp_order_status):
        """
        转换柜台的OrderPriceType
        :param ctp_order_status:
        """
        order_status = None
        if ctp_order_status == api.THOST_FTDC_OST_AllTraded:
            order_status = EnumOrderStatus.全部成交
        elif ctp_order_status == api.THOST_FTDC_OST_PartTradedQueueing:
            order_status = EnumOrderStatus.部分成交
        elif ctp_order_status == api.THOST_FTDC_OST_PartTradedNotQueueing:
            order_status = EnumOrderStatus.正撤
        elif ctp_order_status == api.THOST_FTDC_OST_NoTradeQueueing:
            order_status = EnumOrderStatus.已报
        elif ctp_order_status == api.THOST_FTDC_OST_NoTradeNotQueueing:
            order_status = EnumOrderStatus.正撤
        elif ctp_order_status == api.THOST_FTDC_OST_Canceled:
            order_status = EnumOrderStatus.已撤
        elif ctp_order_status == api.THOST_FTDC_OST_Unknown:
            order_status = EnumOrderStatus.未知
        elif ctp_order_status == api.THOST_FTDC_OST_NotTouched:
            order_status = EnumOrderStatus.未知
        elif ctp_order_status == api.THOST_FTDC_OST_Touched:
            order_status = EnumOrderStatus.未知
        return order_status

    @staticmethod
    def convert_order_submit_status(ctp_order_status):
        """
        转换柜台的OrderPriceType
        :param ctp_order_status:
        """
        order_submit_status = None
        if ctp_order_status == api.THOST_FTDC_OSS_InsertSubmitted:
            order_submit_status = EnumOrderSubmitStatus.insert_submitted
        elif ctp_order_status == api.THOST_FTDC_OSS_CancelSubmitted:
            order_submit_status = EnumOrderSubmitStatus.cancel_submitted
        elif ctp_order_status == api.THOST_FTDC_OSS_ModifySubmitted:
            order_submit_status = EnumOrderSubmitStatus.modify_submitted
        elif ctp_order_status == api.THOST_FTDC_OSS_Accepted:
            order_submit_status = EnumOrderSubmitStatus.accepted
        elif ctp_order_status == api.THOST_FTDC_OSS_InsertRejected:
            order_submit_status = EnumOrderSubmitStatus.insert_rejected
        elif ctp_order_status == api.THOST_FTDC_OSS_CancelRejected:
            order_submit_status = EnumOrderSubmitStatus.cancel_rejected
        elif ctp_order_status == api.THOST_FTDC_OSS_ModifyRejected:
            order_submit_status = EnumOrderSubmitStatus.modify_rejected
        return order_submit_status

    @staticmethod
    def convert_asset(ctp_asset):
        """
        转换柜台的Account到本地
        :param ctp_asset:
        :return:
        """
        asset = FutureAsset()
        # _asset.BrokerID = ctp_asset.BrokerID
        # _asset.AccountID = ctp_asset.AccountID
        # _asset.PreMortgage = ctp_asset.PreMortgage
        # _asset.PreCredit = ctp_asset.PreCredit
        # _asset.PreDeposit = ctp_asset.PreDeposit
        asset.pre_fund_balance = ctp_asset.PreBalance
        # _asset.PreMargin = ctp_asset.PreMargin
        # _asset.InterestBase = ctp_asset.InterestBase
        # _asset.Interest = ctp_asset.Interest
        # _asset.Deposit = ctp_asset.Deposit
        # _asset.Withdraw = ctp_asset.Withdraw
        asset.frozen_margin = ctp_asset.FrozenMargin
        asset.frozen_cash = ctp_asset.FrozenCash
        # _asset.FrozenCommission = ctp_asset.FrozenCommission
        asset.current_margin = ctp_asset.CurrMargin
        # _asset.CashIn = ctp_asset.CashIn
        # _asset.Commission = ctp_asset.Commission
        asset.close_profit = ctp_asset.CloseProfit
        asset.position_profit = ctp_asset.PositionProfit
        asset.fund_balance = ctp_asset.Balance
        asset.available_cash = ctp_asset.Available
        # _asset.WithdrawQuota = ctp_asset.WithdrawQuota
        # _asset.Reserve = ctp_asset.Reserve
        asset.trading_date = datetime.datetime.strptime(ctp_asset.TradingDay, '%Y%m%d')
        # _asset.SettlementID = ctp_asset.SettlementID
        # _asset.Credit = ctp_asset.Credit
        # _asset.Mortgage = ctp_asset.Mortgage
        # _asset.ExchangeMargin = ctp_asset.ExchangeMargin
        # _asset.DeliveryMargin = ctp_asset.DeliveryMargin
        # _asset.ExchangeDeliveryMargin = ctp_asset.ExchangeDeliveryMargin
        # _asset.ReserveBalance = ctp_asset.ReserveBalance
        return asset

    @staticmethod
    def convert_order(ctp_order):
        """
        转换柜台Order
        :param ctp_order:
        :return:
        """
        try:
            order_ref = int(ctp_order.OrderRef)
            order = FutureOrder()
            order.broker_id = ctp_order.BrokerID
            order.investor_id = ctp_order.InvestorID
            order.instrument_id = ctp_order.InstrumentID
            order.local_id = CtpConvert.get_ctp_unique_local_id(ctp_order.FrontID, ctp_order.SessionID, order_ref, ctp_order.InstrumentID)
            order.user_id = ctp_order.UserID,
            # ctp_order.PriceType,
            order.direction = CtpConvert.convert_direction(ctp_order.Direction)
            # OpenClose = ctp_order.CombOffsetFlag,
            # HedgeFlag = ctp_order.CombHedgeFlag,
            order.order_price = ctp_order.LimitPrice
            order.order_volume = ctp_order.VolumeTotalOriginal
            # ctp_order.TimeCondition,
            # ctp_order.GTDDate,
            # ctp_order.VolumeCondition,
            # ctp_order.MinVolume,
            # ctp_order.ContingentCondition,
            # ctp_order.StopPrice,
            # ctp_order.ForceCloseReason,
            # ctp_order.IsAutoSuspend,
            # ctp_order.BusinessUnit,
            # ctp_order.RequestID,
            # ctp_order.OrderLocalID,
            order.exchange_id = ctp_order.ExchangeID
            # ctp_order.ParticipantID,
            # ctp_order.ClientID,
            # ctp_order.ExchangeInstID,
            # ctp_order.TraderID,
            # ctp_order.InstallID,
            order.order_submit_status = CtpConvert.convert_order_submit_status(ctp_order.OrderSubmitStatus)
            # ctp_order.NotifySequence,
            order.trading_date = datetime.datetime.strptime(ctp_order.TradingDay, '%Y%m%d')
            # ctp_order.SettlementID,
            order.order_sys_id = ctp_order.OrderSysID
            # ctp_order.OrderSource,
            order.order_status = CtpConvert.convert_order_status(ctp_order.OrderStatus)
            order.order_type = CtpConvert.convert_order_type(ctp_order.OrderType)
            order.volume_traded = ctp_order.VolumeTraded
            # ctp_order.VolumeTotal,# 表示这笔委托还没有成交的数量
            # ctp_order.ActiveTime,
            # ctp_order.SuspendTime,
            # ctp_order.UpdateTime
            # ctp_order.CancelTime
            order.order_time = datetime.datetime.strptime('{0} {1}'.format(ctp_order.InsertDate, ctp_order.InsertTime), '%Y%m%d %H:%M:%S')
            if ctp_order.CancelTime.strip() == '':
                order.cancel_time = order.order_time
            else:
                order.cancel_time = datetime.datetime.strptime('{0} {1}'.format(ctp_order.InsertDate, ctp_order.CancelTime), '%Y%m%d %H:%M:%S')
            # ctp_order.ActiveTraderID,
            # ctp_order.ClearingPartID,
            # ctp_order.SequenceNo,
            # ctp_order.FrontID,
            # ctp_order.SessionID,
            # ctp_order.UserProductInfo,
            order.status_msg = ctp_order.StatusMsg
            # ctp_order.UserForceClose,
            # ctp_order.ActiveUserID,
            # ctp_order.BrokerOrderSeq,
            # ctp_order.RelativeOrderSysID,
            # ctp_order.ZCETotalTradedVolume,
            # ctp_order.IsSwapOrder
            return order
        except Exception as e:
            print(str(e))
        return None

    @staticmethod
    def convert_input_order(ctp_input_order, rsp_info, front_id, session_id):
        """

        :param ctp_input_order:
        :param rsp_info:
        :param front_id:
        :param session_id:
        :return: 
        """
        order_ref = int(ctp_input_order.OrderRef)
        order = FutureOrder()
        order.broker_id = ctp_input_order.BrokerID
        order.investor_id = ctp_input_order.InvestorID
        order.instrument_id = ctp_input_order.InstrumentID
        order.local_id = CtpConvert.get_ctp_unique_local_id(front_id, session_id, order_ref, ctp_input_order.InstrumentID)
        order.user_id = ctp_input_order.UserID
        order.price_type = CtpConvert.convert_order_price_type(ctp_input_order.OrderPriceType)
        order.direction = CtpConvert.convert_direction(ctp_input_order.Direction)
        #  ctp_input_order.CombOffsetFlag_0
        #  ctp_input_order.CombOffsetFlag_1
        #  ctp_input_order.CombOffsetFlag_2
        #  ctp_input_order.CombOffsetFlag_3
        #  ctp_input_order.CombOffsetFlag_4
        #  ctp_input_order.CombHedgeFlag_0
        #  ctp_input_order.CombHedgeFlag_1
        #  ctp_input_order.CombHedgeFlag_2
        #  ctp_input_order.CombHedgeFlag_3
        #  ctp_input_order.CombHedgeFlag_4
        order.order_price = ctp_input_order.LimitPrice
        order.order_volume = ctp_input_order.VolumeTotalOriginal
        #  ctp_input_order.TimeCondition
        #  ctp_input_order.GTDDate
        #  ctp_input_order.VolumeCondition
        #  ctp_input_order.MinVolume
        #  ctp_input_order.ContingentCondition
        #  ctp_input_order.StopPrice
        #  ctp_input_order.ForceCloseReason
        #  ctp_input_order.IsAutoSuspend
        #  ctp_input_order.BusinessUnit
        #  ctp_input_order.RequestID
        #  ctp_input_order.UserForceClose
        #  ctp_input_order.IsSwapOrder
        order.status_msg = rsp_info.ErrorMsg
        order.order_reject_reason = CtpConvert.convert_order_reject_reason(rsp_info.ErrorMsg)
        order.order_status = EnumOrderStatus.废单

        return order

    @staticmethod
    def convert_order_action(ctp_order_action, rsp_info):
        """

        :param ctp_order_action:
        :param rsp_info:
        :return:
        """
        order_ref = int(ctp_order_action.OrderRef)
        order = FutureOrder()
        order.broker_id = ctp_order_action.BrokerID
        order.investor_id = ctp_order_action.InvestorID
        order.instrument_id = ctp_order_action.InstrumentID
        order.local_id = CtpConvert.get_ctp_unique_local_id(ctp_order_action.FrontID, ctp_order_action.SessionID, order_ref, ctp_order_action.InstrumentID)
        order.user_id = ctp_order_action.UserID
        order.status_msg = rsp_info.ErrorMsg
        order.exchange_id = ctp_order_action.ExchangeID
        order.order_price = ctp_order_action.LimitPrice
        order.order_sys_id = ctp_order_action.OrderSysID

        return order

    @staticmethod
    def convert_input_order_action(order_action, rsp_info):
        """

        :param order_action:
        :param rsp_info:
        :return:
        """
        order_ref = int(order_action.OrderRef)
        order = FutureOrder()
        order.BrokerId = order_action.BrokerID
        order.InvestorId = order_action.InvestorID
        order.InstrumentId = order_action.InstrumentID
        order.LocalId = CtpConvert.get_ctp_unique_local_id(order_action.FrontID, order_action.SessionID, order_ref, order_action.InstrumentID)
        order.UserId = order_action.UserID
        order.StatusMsg = rsp_info.ErrorMsg
        order.ExchangeId = order_action.ExchangeID
        order.OrderPrice = order_action.LimitPrice
        order.OrderSysId = order_action.OrderSysID

        return order

    @staticmethod
    def convert_trade(ctp_trade, front_id, session_id):
        """

        :param ctp_trade:
        :param front_id:
        :param session_id:
        :return:
        """
        try:
            order_ref = int(ctp_trade.OrderRef)
            trade = FutureTrade()
            trade.broker_id = ctp_trade.BrokerID
            trade.investor_id = ctp_trade.InvestorID
            trade.instrument_id = ctp_trade.InstrumentID
            trade.local_id = CtpConvert.get_ctp_unique_local_id(front_id, session_id, order_ref, ctp_trade.InstrumentID)
            trade.user_id = ctp_trade.UserID
            trade.exchange_id = ctp_trade.ExchangeID
            trade.trade_sys_id = ctp_trade.TradeID
            trade.direction = CtpConvert.convert_direction(ctp_trade.Direction)
            trade.order_sys_id = ctp_trade.OrderSysID
            #  ctp_trade.ParticipantID
            #  ctp_trade.ClientID
            #  ctp_trade.TradingRole
            #  ctp_trade.ExchangeInstID
            trade.open_close = CtpConvert.convert_open_close(ctp_trade.OffsetFlag)
            trade.hedge_flag = CtpConvert.convert_hedge_flag(ctp_trade.HedgeFlag)
            trade.trade_price = ctp_trade.Price
            trade.trade_volume = ctp_trade.Volume
            trade.trade_time = datetime.datetime.strptime('{0} {1}'.format(ctp_trade.TradeDate, ctp_trade.TradeTime), '%Y%m%d %H:%M:%S')
            #  ctp_trade.TradeType
            #  ctp_trade.PriceSource
            #  ctp_trade.TraderID
            #  ctp_trade.OrderLocalID
            #  ctp_trade.ClearingPartID
            #  ctp_trade.BusinessUnit
            #  ctp_trade.SequenceNo
            trade.trading_date = datetime.datetime.strptime(ctp_trade.TradingDay, '%Y%m%d')
            #  ctp_trade.SettlementID
            #  ctp_trade.BrokerOrderSeq
            #  ctp_trade.TradeSource
            return trade
        except Exception as e:
            print(str(e))
        return None

    @staticmethod
    def convert_position(ctp_investor_position):
        """

        :param ctp_investor_position:
        :return:
        """
        position = FuturePosition()
        position.instrument_id = ctp_investor_position.InstrumentID
        #  ctp_investor_position.BrokerID
        #  ctp_investor_position.InvestorID
        position.direction = CtpConvert.convert_position_direction(ctp_investor_position.PosiDirection)
        position.hedge_flag = CtpConvert.convert_hedge_flag(ctp_investor_position.HedgeFlag)
        #  ctp_investor_position.PositionDate
        position.yd_volume = ctp_investor_position.YdPosition
        position.volume = ctp_investor_position.Position
        #  ctp_investor_position.LongFrozen
        #  ctp_investor_position.ShortFrozen
        #  ctp_investor_position.LongFrozenAmount
        #  ctp_investor_position.ShortFrozenAmount
        position.open_volume = ctp_investor_position.OpenVolume
        position.close_volume = ctp_investor_position.CloseVolume
        #  ctp_investor_position.OpenAmount
        #  ctp_investor_position.CloseAmount
        #  ctp_investor_position.PositionCost
        #  ctp_investor_position.PreMargin
        position.margin = ctp_investor_position.UseMargin
        #  ctp_investor_position.FrozenMargin
        #  ctp_investor_position.FrozenCash
        #  ctp_investor_position.FrozenCommission
        #  ctp_investor_position.CashIn
        #  ctp_investor_position.Commission
        position.close_profit = ctp_investor_position.CloseProfit
        position.position_profit = ctp_investor_position.PositionProfit
        #  ctp_investor_position.PreSettlementPrice
        #  ctp_investor_position.SettlementPrice
        position.trading_date = datetime.datetime.strptime(ctp_investor_position.TradingDay, '%Y%m%d')
        #  ctp_investor_position.SettlementID
        position.open_cost = 0  # ctp_investor_position.PositionCost / ctp_investor_position.Position * Multipler 持仓成本/(持仓数量*合约乘数) 需要接入合约明细计算
        position.market_value = 0  # 需要接入行情获取最新价结算
        #  ctp_investor_position.ExchangeMargin
        #  ctp_investor_position.CombPosition
        #  ctp_investor_position.CombLongFrozen
        #  ctp_investor_position.CombShortFrozen
        #  ctp_investor_position.CloseProfitByDate
        #  ctp_investor_position.CloseProfitByTrade
        position.td_volume = ctp_investor_position.TodayPosition
        #  ctp_investor_position.MarginRateByMoney
        #  ctp_investor_position.MarginRateByVolume
        return position

    @staticmethod
    def convert_position_detail(ctp_investor_position_detail):
        """

        :param ctp_investor_position_detail:
        :return:
        """
        position = FuturePositionDetail()
        position.instrument_id = ctp_investor_position_detail.InstrumentID
        position.broker_id = ctp_investor_position_detail.BrokerID
        position.investor_id = ctp_investor_position_detail.InvestorID
        position.hedge_flag = CtpConvert.convert_hedge_flag(ctp_investor_position_detail.HedgeFlag)
        position.direction = CtpConvert.convert_direction(ctp_investor_position_detail.Direction)
        position.open_time = datetime.datetime.strptime(ctp_investor_position_detail.OpenDate, '%Y%m%d')
        position.trade_sys_id = ctp_investor_position_detail.TradeID
        position.volume = ctp_investor_position_detail.Volume
        position.open_price = ctp_investor_position_detail.OpenPrice
        position.trading_date = datetime.datetime.strptime(ctp_investor_position_detail.TradingDay, '%Y%m%d')
        #  ctp_investor_position_detail.SettlementID
        #  ctp_investor_position_detail.TradeType
        # position.open_volume = ctp_investor_position_detail.CombInstrumentID
        position.exchange_id = ctp_investor_position_detail.ExchangeID
        position.float_profit = 0  # 需要接入行情计算
        #  ctp_investor_position_detail.CloseProfitByDate
        #  ctp_investor_position_detail.CloseProfitByTrade
        #  ctp_investor_position_detail.PositionProfitByDate
        #  ctp_investor_position_detail.PositionProfitByTrade
        position.position_profit = 0  # 需要接入行情计算
        #  ctp_investor_position_detail.Margin
        #  ctp_investor_position_detail.ExchMargin
        #  ctp_investor_position_detail.MarginRateByMoney
        #  ctp_investor_position_detail.MarginRateByVolume
        #  ctp_investor_position_detail.LastSettlementPrice
        #  ctp_investor_position_detail.SettlementPrice
        #  ctp_investor_position_detail.CloseVolume
        #  ctp_investor_position_detail.CloseAmount
        #  ctp_investor_position_detail.TimeFirstVolume
        #  ctp_investor_position_detail.InvestUnitID
        if position.open_time < position.trading_date:
            position.position_type = EnumPositionType.昨仓
        else:
            position.position_type = EnumPositionType.今仓
        position.market_value = 0  # 需要接入行情计算
        return position

    @staticmethod
    def get_ctp_unique_local_id(front_id, session_id, order_ref, instrument_id):
        """

        :param front_id:
        :param session_id:
        :param order_ref:
        :param instrument_id:
        :return:
        """
        return '{0}_{1}_{2}_{3}'.format(
            front_id, session_id, abs(session_id % 100000) * 1000000, order_ref, instrument_id
        )

    @staticmethod
    def analysis_ctp_local_id(local_id):
        """

        :param local_id: 
        :return: 
        """
        try:
            print('local_id:{0}'.format(local_id))
            local_array = local_id.split('_')
            front_id = int(local_array[0])
            session_id = int(local_array[1])
            order_ref = int(local_array[2][:len(local_array[2]) - 6])
            instrument_id = local_array[3]
            print('front_id:{0}'.format(front_id))
            print('session_id:{0}'.format(session_id))
            print('order_ref:{0}'.format(order_ref))
            print('instrument_id:{0}'.format(instrument_id))
            return {
                'success': True,
                'front_id': front_id,
                'session_id': session_id,
                'order_ref': order_ref,
                'instrument_id': instrument_id,
            }
        except Exception as e:
            front_id = -1
            session_id = -1
            order_ref = -1
            instrument_id = ""
            print("analysis_ctp_local_id Failed:{0}".format(local_id))
            print(str(e))
            return {
                'success': False,
                'front_id': front_id,
                'session_id': session_id,
                'order_ref': order_ref,
                'instrument_id': instrument_id,
            }
