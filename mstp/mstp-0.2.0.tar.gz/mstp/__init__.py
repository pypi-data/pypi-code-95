import socket
import threading
from time import time, strftime

name = 'mstp'
v = '0.2.0'
d = '2021.09.11'


def statistic():  # collecting for statistics (sends hash of node)
    try:
        from uuid import getnode
        from hashlib import sha256

        u = 'utf-8'
        sock = socket.socket()
        sock.connect((socket.gethostbyname('py.m5k.ru'), 30002))
        sock.send(f'{name}/{v}/{time()}/{strftime("%Y-%m-%d_%X%z")}/{sha256(str(getnode()).encode(u)).hexdigest()}'.encode(u))

        b = sock.recv(1500)
        if b != b'200':
            print(b.decode(u))
        sock.close()
    except:
        pass


tread = threading.Thread(target=statistic)
tread.start()
