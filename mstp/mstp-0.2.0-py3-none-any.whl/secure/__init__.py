import socket
from cryptography.fernet import Fernet  #

__all__ = ['server', 'client']

lu = '0.2.0'
lv = '0'
ld = '2021.09.11'


class dt:  # mstp
    from hashlib import sha256

    def hashe(self, data, encode='utf-8'):
        if encode:
            return self.sha256(data.encode(encode)).hexdigest()
        else:
            return self.sha256(data).hexdigest()

    def __init__(self, sock, encode='utf-8'):
        self.sock = sock
        self.u = encode
        self.v = '0.1'

    def send(self, text):
        self.sock.send(
            f'mstp/{self.v}/s{len(text.encode(self.u)):54}{self.hashe(text.encode(self.u), None)}'.encode(
                self.u) + text.encode(self.u))

    def recv(self):
        b = self.sock.recv(128)

        len_ = int(b.decode(self.u)[10:64])

        while len(b) < len_ + 128:
            b += self.sock.recv(len_ + 128 - len(b))

        assert self.hashe(b[128:], None) == b[64:128].decode(self.u)

        return b.decode(self.u)[128:]

    def send_r(self, data):
        self.sock.send(f'mstp/{self.v}/r{len(data):54}{self.hashe(data, None)}'.encode(self.u) + data)

    def recv_r(self):
        b = self.sock.recv(128)

        len_ = int(b[10:64].decode(self.u))
        while len(b) < len_ + 128:
            b += self.sock.recv(len_ + 128 - len(b))

        assert self.hashe(b[128:], None) == b[64:128].decode(self.u)

        return b[128:]

    def headers(self, pkg):
        pkg = pkg[:128].decode(self.u)
        return {'name': pkg[:4], 'v': float(pkg[5:8]), 'type': pkg[9:10], 'length': int(pkg[10:64]),
                'sha256': pkg[64:128]}


class server(object):
    def __init__(self, ip: str = '', port: int = 9000, key: bytes = b'R6ZsDH2OJLuSHyHP0_SsG4kQIJQIbxjYMMiOjSA6vCo=', encoding: str = 'utf-8'):
        self.ip = ip
        self.port = port
        self.key = key
        self.u = encoding

    def con(self, sock_addr, function, _r):
        sock, addr = sock_addr

        e = Fernet(self.key)

        send, recv = dt(sock).send, dt(sock).recv
        if _r:
            function(
                lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                lambda: e.decrypt(recv().encode(self.u)).decode(self.u),
                lambda x: dt(sock).send_r(e.encrypt(x)),
                lambda: e.decrypt(dt(sock).recv_r())
            )
        else:
            function(lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                     lambda: e.decrypt(recv().encode(self.u)).decode(self.u))

        sock.close()

    def run(self, function, _r=False):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.ip, self.port))
        s.listen()

        while True:
            self.con(s.accept(), function, _r)


class client(object):
    def __init__(self, ip: str = '', port: int = 9000, key: bytes = b'R6ZsDH2OJLuSHyHP0_SsG4kQIJQIbxjYMMiOjSA6vCo=', encoding: str = 'utf-8'):
        self.ip = ip
        self.port = port
        self.key = key
        self.u = encoding

    def run(self, function, _r=False):
        sock = socket.socket()
        sock.connect((self.ip, self.port))

        e = Fernet(self.key)

        send, recv = dt(sock, self.u).send, dt(sock, self.u).recv
        if _r:
            function(
                lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                lambda: e.decrypt(recv().encode(self.u)).decode(self.u),
                lambda x: dt(sock, self.u).send_r(e.encrypt(x)),
                lambda: e.decrypt(dt(sock, self.u).recv_r())
            )
        else:
            function(lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                     lambda: e.decrypt(recv().encode(self.u)).decode(self.u))

        sock.close()


class info(object):
    def headers(self):
        print("self, ip: str = '', port: int = 9000, key: bytes = b'R6ZsDH2OJLuSHyHP0_SsG4kQIJQIbxjYMMiOjSA6vCo=', encoding: str = 'utf-8'")
