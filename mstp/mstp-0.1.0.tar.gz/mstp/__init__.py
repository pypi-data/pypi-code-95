import socket
from cryptography.fernet import Fernet  #
from random import randint
from base64 import urlsafe_b64encode

__all__ = ['server']


v = '0.1.0'
d = '2021.09.09'


class sc(object):
    class DH_Endpoint(object):
        def __init__(self, public_key1, public_key2, private_key):
            self.public_key1 = public_key1
            self.public_key2 = public_key2
            self.private_key = private_key
            self.full_key = None

        def generate_partial_key(self):
            partial_key = self.public_key1 ** self.private_key
            partial_key = partial_key % self.public_key2
            return partial_key

        def generate_full_key(self, partial_key_r):
            full_key = partial_key_r ** self.private_key
            full_key = full_key % self.public_key2
            self.full_key = full_key
            return full_key

        def encrypt_message(self, message):
            encrypted_message = ""
            key = self.full_key
            for c in message:
                encrypted_message += chr(ord(c) + key)
            return encrypted_message

        def decrypt_message(self, encrypted_message):
            decrypted_message = ""
            key = self.full_key
            for c in encrypted_message:
                decrypted_message += chr(ord(c) - key)
            return decrypted_message

    def conv(self, num, to_base=10, from_base=10):
        if isinstance(num, str):
            n = int(num, from_base)
        else:
            n = int(num)
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        if n < to_base:
            return alphabet[n]
        else:
            return self.conv(n // to_base, to_base) + alphabet[n % to_base]

    class dt:  # mdtp: # msp
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
                f'msp/{self.v}/s{len(text.encode(self.u)):55}{self.hashe(text.encode(self.u), None)}'.encode(
                    self.u) + text.encode(self.u))

        def recv(self):
            b = self.sock.recv(128)
            # assert len(b.split(b'#')) == 4

            len_ = int(b.decode(self.u)[9:64])

            while len(b) < len_ + 128:
                b += self.sock.recv(len_ + 128 - len(b))

            assert self.hashe(b[128:], None) == b[64:128].decode(self.u)

            return b.decode(self.u)[128:]

        def send_r(self, data):
            self.sock.send(f'msp/{self.v}/r{len(data):55}{self.hashe(data, None)}'.encode(self.u) + data)

        def recv_r(self):
            b = self.sock.recv(128)
            # assert len(b.split(b'#')) == 4

            len_ = int(b[9:64].decode(self.u))
            while len(b) < len_ + 128:
                b += self.sock.recv(len_ + 128 - len(b))

            assert self.hashe(b[128:], None) == b[64:128].decode(self.u)

            return b[128:]

        def headers(self, pkg):
            pkg = pkg[:128].decode(self.u)
            return {'name': pkg[:3], 'v': float(pkg[4:7]), 'type': pkg[8:9], 'length': int(pkg[9:64]),
                    'sha256': pkg[64:128]}


class server(object):
    def __init__(self, ip: str = '', port: int = 9000,
                 public_key_length: int = 6, privat_key_length: int = 6, blocks_number: int = 10,
                 default_key: bytes = b'3T4s8mLUkSII-akOqOXf1KEE8zxHBx-dJriHpFeQq-s=', encoding: str = 'utf-8',
                 print_log=False, slash_log=False):
        self.port = port
        self.ip = ip
        self.public_key_length = public_key_length
        self.privat_key_length = privat_key_length
        self.blocks_number = blocks_number
        self.de = Fernet(default_key)
        self.u = encoding
        self.print_log = print_log
        self.slash_log = slash_log
        if print_log:
            self.print = print
        else:
            self.print = lambda *args, end='': None

    def con(self, sock_addr, function, _r):
        public_keys = [randint(10 ** (self.public_key_length - 1), 10 ** self.public_key_length - 1) for _ in range(self.blocks_number)]
        privat_keys = [randint(10 ** (self.privat_key_length - 1), 10 ** self.privat_key_length - 1) for _ in range(self.blocks_number)]
        self.print(public_keys)
        self.print(privat_keys)
        ms = sc().conv('a'.join([str(b) for b in public_keys]), 36, 11)
        self.print(ms)
        self.print()

        sock, addr = sock_addr
        send, recv = sc().dt(sock).send, sc().dt(sock).recv
        esend, erecv = lambda x: send(self.de.encrypt(x.encode(self.u)).decode(self.u)), lambda: self.de.decrypt(recv().encode(self.u)).decode(self.u)

        # public keys exchange
        b = erecv()
        self.print(b)
        esend(ms)
        oth_public_keys = [int(b) for b in sc().conv(b, 11, 36).split('a')]
        self.print(oth_public_keys)
        self.print()

        # generating half keys
        keys_vars = []
        for i in range(self.blocks_number):
            keys_vars.append(sc().DH_Endpoint(public_keys[i], oth_public_keys[i], privat_keys[i]))

        half_keys = []
        for i in range(self.blocks_number):
            if self.print_log or self.slash_log:
                print(f'\r{i} / {self.blocks_number}', end='')
            half_keys.append(keys_vars[i].generate_partial_key())
        if self.print_log or self.slash_log:
            print(f'\r{self.blocks_number} / {self.blocks_number} done')

        self.print('p', half_keys)
        self.print()

        # half keys exchange
        ms = sc().conv('a'.join([str(b) for b in half_keys]), 36, 11)
        self.print(ms)
        b = erecv()
        self.print(b)
        esend(ms)
        oth_half_keys = [int(b) for b in sc().conv(b, 11, 36).split('a')]
        self.print(oth_half_keys)
        self.print()

        # generating full keys
        full_keys = []
        for i in range(self.blocks_number):
            if self.print_log or self.slash_log:
                print(f'\r{i} / {self.blocks_number}', end='')
            full_keys.append(keys_vars[i].generate_full_key(oth_half_keys[i]))
        if self.print_log or self.slash_log:
            print(f'\r{self.blocks_number} / {self.blocks_number} done')

        self.print(full_keys)

        k = urlsafe_b64encode((sc().conv('a'.join([str(b) for b in full_keys]), 36, 11)[:32]).encode(self.u))
        self.print(k)
        self.print(len(k))
        e = Fernet(k)

        # ################
        if _r:
            function(
                lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                lambda: e.decrypt(recv().encode(self.u)).decode(self.u),
                lambda x: sc().dt(sock).send_r(e.encrypt(x)),
                lambda: e.decrypt(sc().dt(sock).recv_r())
            )
        else:
            function(lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)), lambda: e.decrypt(recv().encode(self.u)).decode(self.u))
        # ################

        sock.close()

    def run(self, function, _r=False):

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.ip, self.port))
        s.listen()

        while True:
            self.con(s.accept(), function, _r)


class client(object):
    def __init__(self, ip: str = '', port: int = 9000,
                 public_key_length: int = 6, privat_key_length: int = 6, blocks_number: int = 10,
                 default_key: bytes = b'3T4s8mLUkSII-akOqOXf1KEE8zxHBx-dJriHpFeQq-s=', encoding: str = 'utf-8',
                 print_log=False, slash_log=True):
        self.port = port
        self.ip = ip
        self.public_key_length = public_key_length
        self.privat_key_length = privat_key_length
        self.blocks_number = blocks_number
        self.de = Fernet(default_key)
        self.u = encoding
        self.print_log = print_log
        self.slash_log = slash_log
        if print_log:
            self.print = print
        else:
            self.print = lambda *args, end='': None

    def con(self, function, _r):
        public_keys = [randint(10 ** (self.public_key_length - 1), 10 ** self.public_key_length - 1) for _ in range(self.blocks_number)]
        privat_keys = [randint(10 ** (self.privat_key_length - 1), 10 ** self.privat_key_length - 1) for _ in range(self.blocks_number)]
        self.print(public_keys)
        self.print(privat_keys)
        ms = sc().conv('a'.join([str(b) for b in public_keys]), 36, 11)
        self.print(ms)
        self.print()

        sock = socket.socket()
        sock.connect(('', 9000))

        send, recv = sc().dt(sock).send, sc().dt(sock).recv
        esend, erecv = lambda x: send(self.de.encrypt(x.encode(self.u)).decode(self.u)), lambda: self.de.decrypt(recv().encode(self.u)).decode(self.u)

        # public keys exchange
        self.print('public keys exchange')
        esend(ms)
        b = erecv()
        self.print(b)
        oth_public_keys = [int(b) for b in sc().conv(b, 11, 36).split('a')]
        self.print(oth_public_keys)
        self.print()

        # generating half keys
        self.print('generating half keys')
        keys_vars = []
        for i in range(self.blocks_number):
            keys_vars.append(sc().DH_Endpoint(oth_public_keys[i], public_keys[i], privat_keys[i]))

        half_keys = []
        for i in range(self.blocks_number):
            if self.print_log or self.slash_log:
                print(f'\r{i} / {self.blocks_number}', end='')
            half_keys.append(keys_vars[i].generate_partial_key())

        if self.print_log or self.slash_log:
            print(f'\r{self.blocks_number} / {self.blocks_number} done')

        self.print('p:', half_keys)
        self.print()

        # half keys exchange
        self.print('half keys exchange')
        ms = sc().conv('a'.join([str(b) for b in half_keys]), 36, 11)
        self.print(ms)
        esend(ms)
        b = erecv()
        self.print(b)
        oth_half_keys = [int(b) for b in sc().conv(b, 11, 36).split('a')]
        self.print(oth_half_keys)
        self.print()

        # generating full keys
        self.print('generating full keys')
        full_keys = []
        for i in range(self.blocks_number):
            if self.print_log or self.slash_log:
                print(f'\r{i} / {self.blocks_number}', end='')
            full_keys.append(keys_vars[i].generate_full_key(oth_half_keys[i]))
        if self.print_log or self.slash_log:
            print(f'\r{self.blocks_number} / {self.blocks_number} done')

        self.print(full_keys)

        k = urlsafe_b64encode((sc().conv('a'.join([str(b) for b in full_keys]), 36, 11)[:32]).encode(self.u))
        self.print(k)
        self.print(len(k))
        e = Fernet(k)

        # ################
        if _r:
            function(
                lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                lambda: e.decrypt(recv().encode(self.u)).decode(self.u),
                lambda x: sc().dt(sock).send_r(e.encrypt(x)),
                lambda: e.decrypt(sc().dt(sock).recv_r())
            )
        else:
            function(lambda x: send(e.encrypt(x.encode(self.u)).decode(self.u)),
                     lambda: e.decrypt(recv().encode(self.u)).decode(self.u))
        # ################

        sock.close()

    def run(self, function, _r=False):
        self.con(function, _r)
