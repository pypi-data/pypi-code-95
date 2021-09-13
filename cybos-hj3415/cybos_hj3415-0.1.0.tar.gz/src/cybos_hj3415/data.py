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
        s = ''
        s += f'현재가 : {self.cur}\n'
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
