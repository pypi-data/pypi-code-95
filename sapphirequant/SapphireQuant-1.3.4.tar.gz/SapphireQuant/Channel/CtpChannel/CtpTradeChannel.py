import re
import threading
from datetime import datetime

from SapphireQuant.Core.Futures import Future, FutureOrder, FutureAsset

from SapphireQuant.Channel.CtpChannel import thosttraderapi as api

from SapphireQuant.Channel.CtpChannel.CtpConvert import CtpConvert
from SapphireQuant.Core.Enum import EnumBuySell, EnumOpenClose, EnumOrderSubmitStatus, EnumOrderStatus, EnumOrderPriceType


class CtpTradeChannel(api.CThostFtdcTraderSpi):
    """
    CTP交易接口
    """

    def __init__(self, user_id, password, broker_id, auth_code, app_id='client_QiPlatform_1'):
        self._user_id = user_id
        self._password = password
        self._broker_id = broker_id
        self._app_id = app_id
        self._auth_code = auth_code
        self._trade_api = None
        self._trade_spi = None
        self._front_address = None
        self._flow_path = None
        self.is_connected = False
        self.trading_date = None
        self._event = threading.Event()
        self._event.clear()

        self._bind_map = {}
        self._is_front_connected = False
        self._is_authenticate = False
        self._is_login = False
        self._is_settlement_info_confirm = False
        self._settlement_info = None
        self._asset = None
        self._lst_future_info = []
        self._lst_order = []
        self._lst_trade = []
        self._lst_position = []
        self._lst_position_detail = []

        self._max_order_ref = 0
        self._front_id = 0
        self._session_id = 0
        self._request_id = 0
        api.CThostFtdcTraderSpi.__init__(self)

    @property
    def broker_id(self):
        """

        :return:
        """
        return self._broker_id

    def connect(self, front_address, flow_path=None):
        """
        连接前置
        :param front_address:
        :param flow_path:
        """
        print('开始连接期货交易服务器......')
        # print(threading.currentThread().ident)
        if self.is_connected:
            print('交易服务器已连接......')
            return
        self._front_address = front_address
        self._flow_path = flow_path
        if self._flow_path is not None:
            self._trade_api = api.CThostFtdcTraderApi_CreateFtdcTraderApi(self._flow_path)
        else:
            self._trade_api = api.CThostFtdcTraderApi_CreateFtdcTraderApi()
        self._trade_api.RegisterFront(self._front_address)
        self._trade_api.RegisterSpi(self)  # 注册事件类
        self._trade_api.SubscribePrivateTopic(api.THOST_TERT_QUICK)  # 注册公有流
        self._trade_api.SubscribePublicTopic(api.THOST_TERT_QUICK)  # 注册私有流
        # 连接前置服务器
        front_flag = self._connect_front()
        if not front_flag:
            return False

        # 看穿认证
        authenticate_flag = self._req_authenticate()
        if not authenticate_flag:
            return False

        # 登录
        login_flag = self._req_login()
        if not login_flag:
            return False

        # 确认结算单
        settlement_info = self.query_settlement_info(self.trading_date)
        if settlement_info is None:
            return False
        settlement_info_confirm_flag = self._req_settlement_info_confirm()
        if not settlement_info_confirm_flag:
            return False
        self.is_connected = True
        print('交易句柄初始化完毕......')
        return True

    def _connect_front(self):
        self._is_front_connected = False
        self._trade_api.Init()
        self._event.clear()
        if self._event.wait(5):
            return self._is_front_connected

        print('前置交易服务器连接超时.....')
        return False

    def _req_authenticate(self):
        self._is_authenticate = False
        auth_field = api.CThostFtdcReqAuthenticateField()
        auth_field.BrokerID = self._broker_id
        auth_field.UserID = self._user_id
        auth_field.AppID = self._app_id
        auth_field.AuthCode = self._auth_code
        print("看穿认证:BrokerID:{0},UserID:{1},APPID:{2},认证码:{3}......".format(self._broker_id, self._user_id, self._app_id, self._auth_code))
        self._trade_api.ReqAuthenticate(auth_field, 0)
        self._event.clear()
        if self._event.wait(5):
            return self._is_authenticate

        print('看穿认证超时.....')
        return False

    def _req_login(self):
        self._is_login = False
        login_field = api.CThostFtdcReqUserLoginField()
        login_field.BrokerID = self._broker_id
        login_field.UserID = self._user_id
        login_field.Password = self._password
        login_field.UserProductInfo = "sapphire"
        print('请求登录服务器......')
        self._trade_api.ReqUserLogin(login_field, 0)
        self._event.clear()
        if self._event.wait(5):
            return self._is_login

        print('登录服务器超时.....')
        return False

    def _req_settlement_info_confirm(self):
        print('发送确认结算单指令......')
        p_settlement_info_confirm = api.CThostFtdcSettlementInfoConfirmField()
        p_settlement_info_confirm.BrokerID = self._broker_id
        p_settlement_info_confirm.InvestorID = self._user_id
        rtn = self._trade_api.ReqSettlementInfoConfirm(p_settlement_info_confirm, 0)
        if rtn != 0:
            print("发送确认结算单指令失败:{0}".format(rtn))
            return False
        else:
            print("发送确认结算单指令成功......")
            self._event.clear()
            if self._event.wait(5):
                return self._is_settlement_info_confirm

            print('确认结算单超时.....')
            return False

    def dis_connect(self):
        """
        断开连接
        """
        print('开始断开期货交易服务器......')
        logout_field = api.CThostFtdcUserLogoutField()
        logout_field.BrokerID = self._broker_id
        logout_field.UserID = self._user_id
        print('请求登出服务器......')
        rtn = self._trade_api.ReqUserLogout(logout_field, 0)
        if rtn != 0:
            print("发送登出请求失败:{0}".format(rtn))

    def OnFrontConnected(self):

        """
        连接交易服务器回调函数
        """
        print("连接交易服务器成功回调......")
        self._is_front_connected = True
        self._event.set()

    def OnFrontDisconnected(self, nReason):
        """
        交易前置服务器断开连接响应
        :param nReason:
        """
        print('交易服务器断开:{0}'.format(nReason))

    def OnRspAuthenticate(self, pRspAuthenticateField, pRspInfo, nRequestID, bIsLast):
        """
        看穿认证回调
        :param pRspAuthenticateField:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('看穿认证失败:{0}'.format(pRspInfo.ErrorMsg))
            self._is_authenticate = False
            self._event.set()
            return
        if bIsLast:
            print('看穿认证成功:{0}'.format(pRspInfo.ErrorMsg))
            self._is_authenticate = True
            self._event.set()

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        """
        用户登录回调函数
        :param pRspUserLogin:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('登录失败:{0}'.format(pRspInfo.ErrorMsg))
            self._is_login = False
            self._event.set()
            return
        if bIsLast:
            self._max_order_ref = int(pRspUserLogin.MaxOrderRef)
            self._front_id = pRspUserLogin.FrontID
            self._session_id = pRspUserLogin.SessionID
            self.trading_date = datetime.strptime(pRspUserLogin.TradingDay, '%Y%m%d')
            print('登录交易服务器成功......')
            print('从CTP交易系统获得交易日信息【{0}】'.format(pRspUserLogin.TradingDay))
            print('从CTP交易系统获得MaxOrderRef:{0},FrontId:{1},SessionId:{2}'.format(pRspUserLogin.MaxOrderRef, pRspUserLogin.FrontID, pRspUserLogin.SessionID))
            self._is_login = True
            self._event.set()

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        """
        客户端登出响应
        :param pUserLogout:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('登出失败:{0}'.format(pRspInfo.ErrorMsg))
            return
        if bIsLast:
            self.is_connected = False
            print('登出成功:BrokerID:{0},UserID:{1}'.format(pUserLogout.BrokerID, pUserLogout.UserID))
            print('释放交易句柄......')
            self._trade_api.Release()

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        """
        请求结算单回调函数
        :param pSettlementInfo:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('请求结算单失败:{0}'.format(pRspInfo.ErrorMsg))
            self._settlement_info = None
            self._event.set()
            return
        if pSettlementInfo is not None and pSettlementInfo.Content is not None:
            self._settlement_info += pSettlementInfo.Content
        if bIsLast:
            print('请求结算单成功......')
            self._event.set()

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        """
        确认结算单回调
        :param pSettlementInfoConfirm:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('确认结算单失败:{0}'.format(pRspInfo.ErrorMsg))
            self._is_settlement_info_confirm = False
            self._event.set()
            return
        if bIsLast:
            print('确认结算单成功......')
            self._is_settlement_info_confirm = True
            self._event.set()

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        """
        查询合约回报
        :param pInstrument:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询合约出错:{0}......'.format(pRspInfo.ErrorMsg))
            self._lst_future_info = None
            self._event.set()
            return
        try:
            future = Future()
            future.id = pInstrument.InstrumentID
            future.name = pInstrument.InstrumentName
            future.exchange_id = pInstrument.ExchangeID
            if pInstrument.ExpireDate is not None and pInstrument.ExpireDate != '':
                future.expire_date = datetime.strptime(pInstrument.ExpireDate, '%Y%m%d')
            if pInstrument.OpenDate is not None and pInstrument.OpenDate != '':
                future.open_date = datetime.strptime(pInstrument.OpenDate, '%Y%m%d')
            future.long_margin_ratio = pInstrument.LongMarginRatio
            future.short_margin_ratio = pInstrument.ShortMarginRatio
            future.product_id = pInstrument.ProductID
            future.volume_multiple = pInstrument.VolumeMultiple
            future.price_tick = pInstrument.PriceTick
            future.product_class = CtpConvert.convert_product_class(pInstrument.ProductClass)
            self._lst_future_info.append(future)
        except Exception as e:
            print('{0}:{1}'.format(pInstrument.InstrumentID, str(e)))
        if bIsLast:
            self._event.set()
            print('查询合约完毕......')

    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        """
        查询账户资金响应
        :param pTradingAccount:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        print('接收到查询账户资金的回报')
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询账户资金失败:{0}'.format(pRspInfo.ErrorMsg))
            self._asset = None
            self._event.set()
            return
        if bIsLast:
            print('查询账户资金成功......')
            self._asset = CtpConvert.convert_asset(pTradingAccount)
            self._event.set()

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        """
        查询委托回报
        :param pOrder:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询委托失败:{0}'.format(pRspInfo.ErrorMsg))
            self._lst_order = None
            self._event.set()
            return
        if pOrder is None:
            if bIsLast:
                print('共查询到:0个委托记录......')
                self._event.set()
            return
        order = CtpConvert.convert_order(pOrder)
        if order is None:
            return
        order.guid = self.bind_attached_info(order.local_id)
        self._lst_order.append(order)
        if bIsLast:
            print('共查询到:{0}个委托记录......'.format(len(self._lst_order)))
            self._event.set()

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        """
        查询委托回报
        :param pTrade:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询成交失败:{0}'.format(pRspInfo.ErrorMsg))
            self._lst_trade = None
            self._event.set()
            return
        if pTrade is None:
            if bIsLast:
                print('共查询到:0个成交记录......')
                self._event.set()
                return
            return
        trade = CtpConvert.convert_trade(pTrade, self._front_id, self._session_id)
        if trade is None:
            return
        trade.guid = self.bind_attached_info(trade.local_id)
        self._lst_trade.append(trade)
        if bIsLast:
            print('共查询到:{0}个成交记录......'.format(len(self._lst_trade)))
            self._event.set()

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        """

        :param pInvestorPosition:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询持仓失败:{0}'.format(pRspInfo.ErrorMsg))
            self._lst_position = None
            self._event.set()
            return
        try:
            if pInvestorPosition is not None:
                self._lst_position.append(CtpConvert.convert_position(pInvestorPosition))
        except Exception as e:
            print(str(e))

        if bIsLast:
            print('共查询到:{0}个持仓记录......'.format(len(self._lst_position)))
            self._event.set()

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        """

        :param pInvestorPositionDetail:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询持仓明细失败:{0}'.format(pRspInfo.ErrorMsg))
            self._lst_position_detail = None
            self._event.set()
            return

        self._lst_position_detail.append(CtpConvert.convert_position_detail(pInvestorPositionDetail))
        if bIsLast:
            print('共查询到:{0}个持仓明细记录......'.format(len(self._lst_position_detail)))
            self._event.set()

    def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
        """

        :param pOrderAction:
        :param pRspInfo:
        :return:
        """
        # 这边只处理了撤单的情况, 没有处理修改委托单的情况, ThostFtdcActionFlagType.Delete
        # 如果交易所认为报单错误，用户就会收到OnErrRtnOrderAction。
        print('OnErrRtnOrderAction回报......')
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('OnErrRtnOrderAction Error:{0}@{1} '.format(pRspInfo.ErrorMsg, pOrderAction.ActionDate) +
                  '{0}:{1},'.format(pOrderAction.ActionTime, pOrderAction.StatusMsg) +
                  '{0}'.format(pOrderAction.OrderActionStatus) +
                  '@BrokerID:{0},InvestorID:{1},UserID:{2},'.format(pOrderAction.BrokerID, pOrderAction.InvestorID, pOrderAction.UserID) +
                  'RequestID:{0}OrderActionRef:{1},'.format(pOrderAction.RequestID, pOrderAction.OrderActionRef) +
                  '{0}_{1}_{2},'.format(pOrderAction.FrontID, pOrderAction.SessionID, pOrderAction.OrderRef) +
                  'OrderSysID:{0},{1}.{2},'.format(pOrderAction.OrderSysID, pOrderAction.InstrumentID, pOrderAction.ExchangeID) +
                  'LimitPrice:{0},VolumeChange:{1},ActionFlag:{2}'.format(pOrderAction.LimitPrice, pOrderAction.VolumeChange, pOrderAction.ActionFlag))
            order = CtpConvert.convert_order_action(pOrderAction, pRspInfo)
            order.guid = self.bind_attached_info(order.local_id)
            # OnFutureOrderCancelFailedEvent?.BeginInvoke(order.Guid.ToString(), pRspInfo.ErrorMsg, null, null);

    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        """

        :param pInputOrderAction:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        # Thost 收到撤单指令，如果没有通过参数校验，拒绝接受撤单指令。用户就会收到OnRspOrderAction 消息，其中包含了错误编码和错误消息。
        print('OnRspOrderAction回报......')
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('OnRspOrderAction Error:{0}'.format(pRspInfo.ErrorMsg) +
                  '@BrokerID:{0},InvestorID:{1},UserID:{2},'.format(pInputOrderAction.BrokerID, pInputOrderAction.InvestorID, pInputOrderAction.UserID) +
                  'RequestID:{0}'.format(pInputOrderAction.RequestID) +
                  'OrderActionRef:{0},'.format(pInputOrderAction.OrderActionRef) +
                  '{0}_{1}_{2},'.format(pInputOrderAction.FrontID, pInputOrderAction.SessionID, pInputOrderAction.OrderRef) +
                  'OrderSysID:{0},{1}.{2},'.format(pInputOrderAction.OrderSysID, pInputOrderAction.InstrumentID, pInputOrderAction.ExchangeID) +
                  'LimitPrice:{0},VolumeChange:{1},ActionFlag:{2}'.format(pInputOrderAction.LimitPrice, pInputOrderAction.VolumeChange, pInputOrderAction.ActionFlag))
            order = CtpConvert.convert_input_order_action(pInputOrderAction, pRspInfo)
            order.guid = self.bind_attached_info(order.local_id)
            # OnFutureOrderCancelFailedEvent?.BeginInvoke(order.Guid.ToString(), pRspInfo.ErrorMsg, null, null);

    def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
        """

        :param pInputOrder:
        :param pRspInfo:
        """
        # 交易所认为报单错误,才触发此回调函数
        print('OnErrRtnOrderInsert回报......')
        order = CtpConvert.convert_input_order(pInputOrder, pRspInfo, self._front_id, self._session_id)
        order.guid = self.bind_attached_info(order.local_id)
        print("OnErrRtnOrderInsert:{0}".format(order.to_string()))
        # OnFutureOrderRejectedEvent?.BeginInvoke(order, null, null);

    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        """

        :param pInputOrder:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        # Thost 收到报单指令，如果没有通过参数校验，拒绝接受报单指令。用户就会收到OnRspOrderInsert 消息，其中包含了错误编码和错误消息。
        # 如果Thost接受了报单指令，用户不会收到OnRspOrderInsert，而会收到OnRtnOrder，
        print('OnRspOrderInsert回报......')
        order = CtpConvert.convert_input_order(pInputOrder, pRspInfo, self._front_id, self._session_id)
        order.guid = self.bind_attached_info(order.local_id)
        print("OnRspOrderInsert:{0}".format(order.to_string()))
        # OnFutureOrderRejectedEvent?.BeginInvoke(order, null, null);

    def OnRtnOrder(self, pOrder):
        """
        委托回报  交易所收到报单后，通过校验。用户会收到 OnRtnOrder。
        :param pOrder:
        :return:
        """
        order = CtpConvert.convert_order(pOrder)
        order.guid = self.bind_attached_info(order.local_id)
        print('OnRtnOrder:{0}'.format(order.to_string()))
        if (order.order_submit_status == EnumOrderSubmitStatus.insert_rejected) or (
                order.order_submit_status == EnumOrderSubmitStatus.cancel_rejected) or (
                order.order_submit_status == EnumOrderSubmitStatus.modify_rejected):
            # OnFutureOrderRejectedEvent?.BeginInvoke(order, null, null)
            return

        if (order.order_submit_status == EnumOrderSubmitStatus.accepted) and (order.order_status == EnumOrderStatus.已撤):
            # OnFutureOrderCanceledEvent?.BeginInvoke(order, null, null);
            return

        # OnFutureOrderEvent?.BeginInvoke(order, null, null);

    def OnRtnTrade(self, pTrade):
        """
        交易所收到报单后，通过校验。用户会收到 OnRtnTrade。
        :param pTrade:
        """
        print('成交回报......')
        trade = CtpConvert.convert_trade(pTrade, self._front_id, self._session_id)
        print('OnRtnTrade:{0}'.format(trade.to_string()))
        trade.guid = self.bind_attached_info(trade.local_id)
        # OnFutureTradeEvent?.BeginInvoke(trade, null, null);

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        """

        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        print('OnRspError:{0}'.format(pRspInfo.ErrorMsg))

    def send_order(self, order):
        """

        :param order:
        """
        self._max_order_ref += 1
        self._request_id += 1
        id = order.instrument_id.split('.')[0]
        order.local_id = CtpConvert.get_ctp_unique_local_id(self._front_id, self._session_id, self._max_order_ref, id)
        self._bind_map[order.local_id] = order.guid

        if order.direction == EnumBuySell.买入:
            ctp_direction = api.THOST_FTDC_D_Buy
        else:
            ctp_direction = api.THOST_FTDC_D_Sell

        if order.open_close == EnumOpenClose.开仓:
            ctp_open_close = '0'
        else:
            ctp_open_close = '1'

        if order.order_price_type == EnumOrderPriceType.市价:
            ctp_order_price_type = api.THOST_FTDC_OPT_AnyPrice
            ctp_limit_price = 0
        elif order.order_price_type == EnumOrderPriceType.限价:
            ctp_order_price_type = api.THOST_FTDC_OPT_LimitPrice
            ctp_limit_price = order.order_price
        else:
            ctp_order_price_type = api.THOST_FTDC_OPT_AnyPrice
            ctp_limit_price = 0

        order_field = api.CThostFtdcInputOrderField()
        order_field.BrokerID = self._broker_id
        order_field.ExchangeID = order.exchange_id
        order_field.InstrumentID = order.instrument_id
        order_field.UserID = self._user_id
        order_field.InvestorID = self._user_id
        order_field.Direction = ctp_direction
        order_field.LimitPrice = ctp_limit_price
        order_field.VolumeTotalOriginal = order.order_volume
        order_field.OrderPriceType = ctp_order_price_type
        order_field.ContingentCondition = api.THOST_FTDC_CC_Immediately  # 立即发单
        order_field.TimeCondition = api.THOST_FTDC_TC_GFD  # 当日有效
        order_field.VolumeCondition = api.THOST_FTDC_VC_AV  # 任何数量
        order_field.CombHedgeFlag = api.THOST_FTDC_BHF_Speculation  # 投机
        order_field.CombOffsetFlag = ctp_open_close
        order_field.GTDDate = ""
        order_field.OrderRef = str(self._max_order_ref)
        order_field.MinVolume = 0
        order_field.ForceCloseReason = api.THOST_FTDC_FCC_NotForceClose
        order_field.IsAutoSuspend = 0
        rtn = self._trade_api.ReqOrderInsert(order_field, self._request_id)
        if rtn != 0:
            print('报单失败......')
        else:
            print('send_order:{0}'.format(order.to_string()))
        return order

    def send_order_limit_price(self, instrument_id, exchange_id, direction, open_close, price, volume):
        """
        限价发单
        :param instrument_id:
        :param exchange_id:
        :param direction:
        :param open_close:
        :param price:
        :param volume:
        """
        order = FutureOrder()
        order.instrument_id = instrument_id
        order.exchange_id = exchange_id
        order.direction = direction
        order.open_close = open_close
        order.order_price = price
        order.order_volume = volume
        order.order_price_type = EnumOrderPriceType.限价
        self.send_order(order)
        return order

    def send_order_any_price(self, instrument_id, exchange_id, direction, open_close, volume):
        """
        市价发单
        :param instrument_id:
        :param exchange_id:
        :param direction:
        :param open_close:
        :param volume:
        """
        order = FutureOrder()
        order.instrument_id = instrument_id
        order.exchange_id = exchange_id
        order.direction = direction
        order.open_close = open_close
        order.order_price = 0
        order.order_volume = volume
        order.order_price_type = EnumOrderPriceType.市价
        self.send_order(order)
        return order

    def cancel_order(self, order):
        """

        :param order:
        """
        print('cancel_order:{0}'.format(order.to_string()))
        self._request_id += 1
        result = CtpConvert.analysis_ctp_local_id(order.local_id)
        if result['success']:
            input_order_action_field = api.CThostFtdcInputOrderActionField()
            input_order_action_field.ActionFlag = api.THOST_FTDC_AF_Delete
            input_order_action_field.BrokerID = self._broker_id
            input_order_action_field.InvestorID = self._user_id
            input_order_action_field.InstrumentID = order.instrument_id
            input_order_action_field.FrontID = result['front_id']
            input_order_action_field.SessionID = result['session_id']
            input_order_action_field.OrderRef = str(result['order_ref'])
            input_order_action_field.ExchangeID = order.exchange_id
            input_order_action_field.OrderSysID = order.order_sys_id
            rtn = self._trade_api.ReqOrderAction(input_order_action_field, self._request_id)
            if rtn != 0:
                print('发送撤单请求失败:{0}'.format(rtn))
        else:
            print('未找到对应委托:{0}'.format(order.local_id))

    def query_instrument(self, instrument_id=None):
        """
        查询柜台合约信息
        :param instrument_id:
        :return:
        """
        self._request_id += 1
        self._lst_future_info = []
        qry_field = api.CThostFtdcQryInstrumentField()
        if instrument_id is not None:
            qry_field.InstrumentID = instrument_id
        rtn = self._trade_api.ReqQryInstrument(qry_field, self._request_id)
        if rtn != 0:
            print('发送查询合约请求失败:{0}'.format(rtn))
            return None

        print('发送查询合约请求成功......')
        self._event.clear()
        if self._event.wait(30):
            return self._lst_future_info

        print('请求查询合约信息超时......')
        return None

    def query_asset(self):
        """
        查询柜台账户资金
        :return:
        """
        self._request_id += 1
        self._asset = None
        qry_asset_field = api.CThostFtdcQryTradingAccountField()
        qry_asset_field.BrokerID = self._broker_id
        qry_asset_field.InvestorID = self._user_id
        rtn = self._trade_api.ReqQryTradingAccount(qry_asset_field, self._request_id)
        if rtn != 0:
            print('发送查询账户资金请求失败:{0}'.format(rtn))
            return None
        print('发送查询账户资金请求成功......')
        self._event.clear()
        if self._event.wait(5):
            return self._asset

        print('请求查询账户超时......')
        return None

    def query_orders(self):
        """

        :return:
        """
        self._request_id += 1
        self._lst_order = []
        qry_field = api.CThostFtdcQryOrderField()
        qry_field.BrokerID = self._broker_id
        qry_field.InvestorID = self._user_id
        rtn = self._trade_api.ReqQryOrder(qry_field, self._request_id)
        if rtn != 0:
            print('发送查询委托请求失败:{0}'.format(rtn))
            return None
        print('发送查询委托请求成功......')
        self._event.clear()
        if self._event.wait(5):
            return self._lst_order

        print('请求查询委托超时......')
        return None

    def query_trades(self):
        """

        :return:
        """
        self._request_id += 1
        self._lst_trade = []
        qry_field = api.CThostFtdcQryTradeField()
        qry_field.BrokerID = self._broker_id
        qry_field.InvestorID = self._user_id
        rtn = self._trade_api.ReqQryTrade(qry_field, self._request_id)
        if rtn != 0:
            print('发送查询成交请求失败:{0}'.format(rtn))
            return None
        print('发送查询成交请求成功......')
        self._event.clear()
        if self._event.wait(5):
            return self._lst_trade

        print('请求查询成交超时......')
        return None

    def query_positions(self):
        """

        :return:
        """
        self._request_id += 1
        self._lst_position = []
        qry_field = api.CThostFtdcQryInvestorPositionField()
        qry_field.BrokerID = self._broker_id
        qry_field.InvestorID = self._user_id
        rtn = self._trade_api.ReqQryInvestorPosition(qry_field, self._request_id)
        if rtn != 0:
            print('发送查询持仓请求失败:{0}'.format(rtn))
            return None
        print('发送查询持仓请求成功......')
        self._event.clear()
        if self._event.wait(5):
            return self._lst_position

        print('请求查询持仓超时......')
        return None

    def query_position_details(self):
        """
        查询持仓明细
        :return:
        """
        self._request_id += 1
        self._lst_position_detail = []
        qry_field = api.CThostFtdcQryInvestorPositionDetailField()
        qry_field.BrokerID = self._broker_id
        qry_field.InvestorID = self._user_id
        rtn = self._trade_api.ReqQryInvestorPositionDetail(qry_field, self._request_id)
        if rtn != 0:
            print('发送查询持仓明细请求失败:{0}'.format(rtn))
            return None
        print('发送查询持仓明细请求成功......')
        self._event.clear()
        if self._event.wait(5):
            return self._lst_position_detail

        print('请求查询持仓明细超时......')
        return None

    def query_settlement_info(self, trading_date):
        """
        请求结算单
        :param trading_date:
        """
        print('发送请求结算单指令......')
        self._settlement_info = ''
        qry_settlement_info_field = api.CThostFtdcQrySettlementInfoField()
        qry_settlement_info_field.BrokerID = self._broker_id
        qry_settlement_info_field.InvestorID = self._user_id
        qry_settlement_info_field.TradingDay = trading_date.strftime('%Y%m%d')
        rtn = self._trade_api.ReqQrySettlementInfo(qry_settlement_info_field, 0)
        if rtn != 0:
            print("发送请求结算单指令失败:{0}".format(rtn))
            return None

        print("发送请求结算单指令成功......")
        self._event.clear()
        if self._event.wait(5):
            return self._settlement_info

        print("请求结算单超时......")
        return None

    def bind_attached_info(self, local_id):
        """
        绑定附加条件
        :param local_id:
        :return:
        """
        guid = None
        if local_id in self._bind_map.keys():
            guid = self._bind_map[local_id]
        return guid

    def query_asset_by_trading_date(self, trading_date):
        """

        :param trading_date:
        :return:
        """
        print('请求结算单:{0}'.format(trading_date.strftime('%Y%m%d')))
        settlement_info = self.query_settlement_info(trading_date)
        asset = FutureAsset()
        asset.trading_date = trading_date
        patt = r'期初结存 Balance b/f：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.pre_fund_balance = float(match_group[0][1])

        patt = r'期末结存 Balance c/f：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.fund_balance = float(match_group[0][1])

        patt = r'手 续 费 Commission：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.fee = float(match_group[0][1])

        patt = r'出 入 金 Deposit/Withdrawal：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.withdrawal = float(match_group[0][1])

        patt = r'交割手续费 Delivery Fee：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.delivery_fee = float(match_group[0][1])

        patt = r'保证金占用 Margin Occupied：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.margin = float(match_group[0][1])

        patt = r'可用资金 Fund Avail.：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.available_cash = float(match_group[0][1])

        patt = r'平仓盈亏 Realized P/L：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.close_profit = float(match_group[0][1])

        patt = r'持仓盯市盈亏 MTM P/L：(\s*?)([-]?[\d]+.[\d]+)'
        match_group = re.findall(patt, settlement_info)
        if match_group is not None and len(match_group) >= 1:
            if len(match_group[0]) >= 2:
                asset.position_profit = float(match_group[0][1])

        return asset
