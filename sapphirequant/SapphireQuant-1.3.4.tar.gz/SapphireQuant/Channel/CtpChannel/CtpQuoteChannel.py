import threading
from datetime import datetime

from SapphireQuant.Channel.CtpChannel import thostmduserapi as api
from SapphireQuant.Channel.CtpChannel.CtpConvert import CtpConvert
from SapphireQuant.Core.Enum import EnumQuoteEventType


class CtpQuoteChannel(api.CThostFtdcMdSpi):
    """
    CTP行情接口
    """

    def __init__(self, user_id, password, broker_id, auth_code, app_id='client_QiPlatform_1'):
        self._on_start_event = []
        self._on_end_event = []
        self._on_bar_event = []
        self._on_tick_event = []
        self._on_day_begin_event = []
        self._on_day_end_event = []
        self._user_id = user_id
        self._password = password
        self._broker_id = broker_id
        self._app_id = app_id
        self._auth_code = auth_code
        self._md_api = None
        self._trade_spi = None
        self._front_address = None
        self._flow_path = None
        self.is_connected = False
        self.trading_date = None
        self._debug_mode = False
        self._event = threading.Event()
        self._event.clear()

        self._is_front_connected = False
        self._is_login = False

        api.CThostFtdcMdSpi.__init__(self)

    def connect(self, front_address, flow_path=None):
        """
        连接前置
        :param front_address:
        :param flow_path:
        """
        print('开始连接期货行情服务器......')
        # print(threading.currentThread().ident)
        if self.is_connected:
            print('行情服务器已连接......')
            return
        self._front_address = front_address
        self._flow_path = flow_path
        if self._flow_path is not None:
            self._md_api = api.CThostFtdcMdApi_CreateFtdcMdApi(self._flow_path)
        else:
            self._md_api = api.CThostFtdcMdApi_CreateFtdcMdApi()
        self._md_api.RegisterFront(self._front_address)
        self._md_api.RegisterSpi(self)  # 注册事件类
        # 连接前置服务器
        front_flag = self._connect_front()
        if not front_flag:
            return False

        # 登录
        login_flag = self._req_login()
        if not login_flag:
            return False
        self.is_connected = True
        print('行情句柄初始化完毕......')
        return True

    def _connect_front(self):
        self._is_front_connected = False
        self._md_api.Init()
        self._event.clear()
        if self._event.wait(10):
            return self._is_front_connected

        print('前置行情服务器连接超时.....')
        return False

    def _req_login(self):
        self._is_login = False
        login_field = api.CThostFtdcReqUserLoginField()
        login_field.BrokerID = self._broker_id
        login_field.UserID = self._user_id
        login_field.Password = self._password
        login_field.UserProductInfo = "sapphire"
        print('请求登录服务器......')
        self._md_api.ReqUserLogin(login_field, 0)
        self._event.clear()
        if self._event.wait(5):
            return self._is_login

        print('登录服务器超时.....')
        return False

    def dis_connect(self):
        """
        断开连接
        """
        print('开始断开期货行情服务器......')
        logout_field = api.CThostFtdcUserLogoutField()
        logout_field.BrokerID = self._broker_id
        logout_field.UserID = self._user_id
        print('请求登出服务器......')
        rtn = self._md_api.ReqUserLogout(logout_field, 0)
        if rtn != 0:
            print("发送登出请求失败:{0}".format(rtn))

    def OnFrontConnected(self):
        """
        连接交易服务器回调函数
        """
        print("连接行情服务器成功回调......")
        self._is_front_connected = True
        self._event.set()

    def OnFrontDisconnected(self, nReason):
        """
        交易前置服务器断开连接响应
        :param nReason:
        """
        print('行情服务器断开:{0}'.format(nReason))

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
            try:
                self.trading_date = datetime.strptime(pRspUserLogin.TradingDay, '%Y%m%d')
                print('登录行情服务器成功......')
                print('从CTP行情系统获得交易日信息【{0}】'.format(pRspUserLogin.TradingDay))
                print('从CTP行情系统获得FrontId:{0},BrokerId:{1},UserId:{2},LoginTime:{3}'.format(pRspUserLogin.FrontID, pRspUserLogin.BrokerID, pRspUserLogin.UserID, pRspUserLogin.LoginTime))
                print('中金所时间:{0},郑商所时间:{1},大商所时间:{2},上期所时间:{3}'.format(pRspUserLogin.FFEXTime, pRspUserLogin.CZCETime, pRspUserLogin.DCETime, pRspUserLogin.SHFETime))
                # OnConnectedEvent?.BeginInvoke(null, null);
            except Exception as e:
                print(str(e))
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
            # OnDisconnectedEvent?.BeginInvoke(null, null);
            print('释放行情句柄......')
            self._md_api.Release()

    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        """

        :param pSpecificInstrument:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('订阅失败:{0}'.format(pRspInfo.ErrorMsg))
            return

        if bIsLast:
            pass

        print('订阅成功:{0}'.format(pSpecificInstrument.InstrumentID))

    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        """

        :param pSpecificInstrument:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('退订失败:{0}'.format(pRspInfo.ErrorMsg))
            return

        if bIsLast:
            pass

        print('退订成功:{0}'.format(pSpecificInstrument.InstrumentID))

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        """

        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        """
        print('OnRspError:{0},ID:{1}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

    def OnHeartBeatWarning(self, nTimeLapse):
        """
        心跳
        :param nTimeLapse:
        """
        print('心跳:{0}'.format(str(nTimeLapse)))

    def OnRtnDepthMarketData(self, pDepthMarketData):
        """
        行情回报
        :param pDepthMarketData:
        :return:
        """
        tick = CtpConvert.convert_tick(pDepthMarketData)
        if abs(tick.open_price) < 0.0000001:
            print('非法Tick(开盘价=0):{0}'.format(tick.to_string()))
            return
        if abs(tick.volume) < 0.0000001:
            print('非法Tick(成交量=0):{0}'.format(tick.to_string()))
            return
        if abs(tick.turnover) < 0.0000001:
            print('非法Tick(成交额=0):{0}'.format(tick.to_string()))
            return
        # print(tick.to_string())
        try:
            for event in self._on_tick_event:
                event(tick)
        except Exception as e:
            print('实盘行情模块：[on_tick]事件异常:{0},Id:{1}'.format(str(e), tick.instrument_id))
            if self._debug_mode:
                raise e

    def subscribe(self, sub_id):
        """
        订阅
        :param sub_id:
        """
        str_array = ";".join(map(str, sub_id))
        print('订阅:{0}个合约:{1}'.format(len(sub_id), str_array))
        self._md_api.SubscribeMarketData([id.encode('utf-8') for id in sub_id], len(sub_id))

    def un_subscribe(self, sub_id):
        """
        退订
        :param sub_id:
        """
        str_array = ";".join(map(str, sub_id))
        print('退订:{0}个合约:{1}'.format(len(sub_id), str_array))
        self._md_api.UnSubscribeMarketData([id.encode('utf-8') for id in sub_id], len(sub_id))

    def register_event(self, event, event_type):
        """
        注册事件
        :param event_type:
        :param event:EnumQuoteEventType
        """
        if event_type == EnumQuoteEventType.on_start:
            self._on_start_event.append(event)
        elif event_type == EnumQuoteEventType.on_end:
            self._on_end_event.append(event)
        elif event_type == EnumQuoteEventType.on_day_begin:
            self._on_day_begin_event.append(event)
        elif event_type == EnumQuoteEventType.on_day_end:
            self._on_day_end_event.append(event)
        elif event_type == EnumQuoteEventType.on_bar:
            self._on_bar_event.append(event)
        elif event_type == EnumQuoteEventType.on_tick:
            self._on_tick_event.append(event)
