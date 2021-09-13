"""

파이썬 cybos 서버를 실행시킨 상태에서 서버와 통신하며 여러 명령어를 실행하는 클라이언트 모듈
"""
from socket import *
import pickle
from . import data

from util_hj3415 import utils

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class Command:
    def __init__(self):
        """

        소켓 통신을 이용하여 cybos 서버에 명령어를 내리는 클래스
        """
        self.addr = (data.SERVER_ADDR, data.TCPPORT)
        print(f'Set server address : {self.addr}')

    def account(self) -> data.AccountData:
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(data.ACC.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            acc_data = pickle.loads(raw_data)

            # 투자종목의 항목들에 대한 여러가지 전처치
            for stock in acc_data.stocks:
                # 종목코드에 A를 빼준다.
                stock['종목코드'] = stock['종목코드'].replace('A', '')
                # 체결장부단가에서 소수점 제거
                stock['체결장부단가'] = int(stock['체결장부단가'])
            logger.info(acc_data)
        finally:
            tcp_sock.close()
        return acc_data

    def _code_manager(self, code: str, cmd: str):
        if not utils.is_6digit(code):
            raise ValueError
        # 소켓은 클래스에서 공통으로 사용하면 에러가 나고 명령어를 보낼때마다 만들어서 사용하고 폐기해야 한다.
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            if cmd not in data.CMANAGER_CMD:
                raise ValueError
            tcp_sock.sendall(f'{data.CMANAGER}/{code}/{cmd}'.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            code_data = pickle.loads(raw_data)
        finally:
            tcp_sock.close()
        return code_data

    def get_name(self, code: str):
        return self._code_manager(code=code, cmd='get_name')

    def get_status(self, code: str):
        return self._code_manager(code=code, cmd='get_status')

    def is_kospi200(self, code: str):
        return self._code_manager(code=code, cmd='is_kospi200')

    def cprice(self, code) -> data.CurrentPriceData:
        if not utils.is_6digit(code):
            raise ValueError
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(f'{data.CPRICE}/{code}'.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            cprice_data = pickle.loads(raw_data)
            logger.info(cprice_data)
        finally:
            tcp_sock.close()
        return cprice_data

    def inquire_order(self) -> list:
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(data.IORDER.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            order_list = pickle.loads(raw_data)
            logger.info(order_list)
        finally:
            tcp_sock.close()
        return order_list

    def buy_order(self, code: str, amount: int, price: int):
        if not utils.is_6digit(code):
            raise ValueError
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(f'{data.BUY}/{code}/{amount}/{price}'.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            result = pickle.loads(raw_data)
            logger.info(result)
        finally:
            tcp_sock.close()

    def sell_order(self, code: str, amount: int, price: int):
        if not utils.is_6digit(code):
            raise ValueError
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(f'{data.SELL}/{code}/{amount}/{price}'.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            result = pickle.loads(raw_data)
            logger.info(result)
        finally:
            tcp_sock.close()

    def cancel_one(self, ordernum: str):
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(f'{data.CANCEL}/one/{ordernum}'.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            result = pickle.loads(raw_data)
            logger.info(result)
        finally:
            tcp_sock.close()

    def cancel_all(self, code: str):
        if not utils.is_6digit(code):
            raise ValueError
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.connect(self.addr)
        try:
            tcp_sock.sendall(f'{data.CANCEL}/all/{code}'.encode())
            raw_data = tcp_sock.recv(data.BUFSIZ)
            result = pickle.loads(raw_data)
            logger.info(result)
        finally:
            tcp_sock.close()
