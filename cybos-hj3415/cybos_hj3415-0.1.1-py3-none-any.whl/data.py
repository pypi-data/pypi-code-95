SERVER_ADDR = '192.168.0.174'
# SERVER_ADDR = 'localhost'


ACC = 'account'
CMANAGER = 'code_manager'
CMANAGER_CMD = ['get_name', 'get_status', 'is_kospi200']
CPRICE = 'current_price'
IORDER = 'inquire_order'
BUY = 'buy_order'
SELL = 'sell_order'
CANCEL = 'cancel_order'


BUFSIZ = 1024
TCPPORT = 21568
UDPPORT = 21567


class CurrentPriceData:
    """

    현재가와 10차 호가를 저장하기 위한 단순 저장소.

    Attributes:
        cur (int): 현재가
        offer (list): 매도호가
        bid (list): 매수호가

    """
    def __init__(self):
        self.cur = 0  # 현재가
        self.offer = []  # 매도호가
        self.bid = []  # 매수호가

    def __str__(self):
        s = f'현재가 : {self.cur}\n'
        for i in range(10):
            s += f"{i + 1}차 매도/매수 호가: {self.offer[i]} {self.bid[i]}\n"
        return s


class AccountData:
    """

    계좌정보와 투자종목의 상태를 저장하는 클래스

    Attributes:
        acc (dict): 계좌정보
        stocks (list): 투자종목

    """
    def __init__(self):
        self.acc = {}
        self.stocks = []

    def __str__(self):
        s = ''
        # 계좌정보
        for k in self.acc.keys():
            s += f'{k}\t'
        s += '\n'
        for v in self.acc.values():
            s += f'{v}\t'
        s += '\n'

        # 투자종목 정보
        if len(self.stocks) > 0:
            for k in self.stocks[0].keys():
                s += f'{k}\t'
            s += '\n'
            for stock in self.stocks:
                for v in stock.values():
                    s += f'{v}\t'
        return s


class StockAd:
    """

    거래소 등락 현황 데이터 (상승, 상한,하한 종목수 등등)을 요청하고 수신합니다.

    Attributes:
        kospi (dict): 상승종목수, 상한종목수, 보합종목수, 하락종목수, 하한종목수, 지수, 전일비, 총거래량, 총거래량전일비, 총거래대금
        kosdaq (dict):  상승종목수, 상한종목수, 보합종목수, 하락종목수, 하한종목수, 총거래량, 총거래대금

    """
    def __init__(self):
        self.kospi = {}
        self.kosdaq = {}

    def __str__(self):
        return str(self.kospi) + r'\n' + str(self.kosdaq)


class Stock:
    """

    종목 세부 사항 클래스

    Attributes:
        순위 (int)
        종목코드 (str)
        종목명 (str)
        현재가 (int)
        전일대비 (int)
        전일대비율 (float)
        거래량 (int)
        거래대금 (int)
    """
    def __init__(self):
        self.순위 = float('nan')
        self.종목코드 = ''
        self.종목명 = ''
        self.현재가 = float('nan')
        self.전일대비 = float('nan')
        self.전일대비율 = float('nan')
        self.거래량 = float('nan')
        self.거래대금 = float('nan')

    def __str__(self):
        s = f'순위 : {self.순위}\n'
        s += f'종목코드 : {self.종목코드}\n'
        s += f'종목명 : {self.종목명}\n'
        s += f'현재가 : {self.현재가}\n'
        s += f'전일대비 : {self.전일대비}\n'
        s += f'전일대비율 : {self.전일대비율}\n'
        s += f'거래량 : {self.거래량}\n'
        s += f'거래대금 : {self.거래대금}'
        return s


class TopDealStocks:
    """

    당일 거래량/거래대금 상위종목을 조회할 수 있습니다.

    Attributes:
        kospi (dict): key - 순위, value - _Stock 인스턴스
        kosdaq (dict):  key - 순위, value - _Stock 인스턴스

    """
    def __init__(self):
        self.top_stocks = {}

    def add(self, stock: Stock):
        self.top_stocks[f'{stock.순위}'] = stock

    def yield_topn(self, n: int):
        for i in range(1, n+1):
            yield self.top_stocks[f'{i}']
