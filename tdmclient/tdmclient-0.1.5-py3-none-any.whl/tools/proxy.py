# This file is part of tdmclient.
# Copyright 2021 ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE,
# Miniature Mobile Robots group, Switzerland
# Author: Yves Piguet
#
# SPDX-License-Identifier: BSD-3-Clause

# file:///C:/Users/piguet/Documents/EPFL/Mobots/vpl-web/index-classic.html?robot=thymio-tdm#w=ws%3A%2F%2Flocalhost%3A8597

import socket
# import websockets
import hashlib
import base64
import threading
import sys

from tdmclient import ThymioFB, FlatBuffer


class WebSocketState:

    def __init__(self, socket, send_mask=False):
        self.socket = socket
        self.input_buffer = b""
        self.send_mask = send_mask
        self.message = b""
        self.text_msg = False
        self.closed = False

    @staticmethod
    def apply_mask(input, masking_key):
        output = b""
        for i in range(len(input)):
            output += bytes((input[i] ^ masking_key[i % 4],))
        return output

    def request(self, n=None):
        if n is None:
            n = len(self.input_buffer) + 1
        while n > len(self.input_buffer):
            self.input_buffer += self.socket.recv(1024)

    def receive(self, n):
        self.request(n)
        data = self.input_buffer[0:n]
        self.input_buffer = self.input_buffer[n:]
        return data

    def receive_packet(self):
        b = self.receive(2)
        self.input_buffer
        fin = (b[0] & 0x80) != 0
        opcode = b[0] & 7
        mask = (b[1] & 0x80) != 0
        payload_len = b[1] & 0x7f
        if payload_len == 126:
            # length is next uint16
            b = self.receive(2)
            payload_len = (b[0] << 8) | b[1]
        elif payload_len == 127:
            # length is next uint64
            b = self.receive(8)
            payload_len = (b[0] << 56) | (b[1] << 48) | (b[2] << 40) | (b[3] << 32) | (b[4] << 24) | (b[5] << 16) | (b[6] << 8) | b[7]
        if mask:
            masking_key = self.receive(4)
        encoded_payload = self.receive(payload_len)
        if mask:
            payload = self.apply_mask(encoded_payload, masking_key)
        else:
            payload = encoded_payload

        # act on command
        is_msg = False
        if opcode == 0:
            # continuation
            self.message += payload
            is_msg = True
        elif opcode == 1:
            # text message
            self.text_msg = True
            self.message = payload
            is_msg = True
        elif opcode == 2:
            # binary message
            self.text_msg = False
            self.message = payload
            is_msg = True
        elif opcode == 8:
            # close
            self.closed = True
        elif opcode == 9:
            # ping
            pong = bytes([b[0] & 0xf0 | 0x0a, b[1]] + encoded_payload)
            self.socket.send(pong)

        if is_msg and fin:
            return str(self.message, "utf-8") if self.text_msg else self.message

    def send_packet(self, payload):
        is_str = isinstance(payload, str)
        payload_bin = bytes(payload, "utf-8") if is_str else payload
        payload_len = len(payload_bin)
        header = bytes((
            0x80 | (0x01 if is_str else 0x02),
            (0x80 if self.send_mask else 0) | (payload_len if payload_len < 126 else 126)
        ))
        if payload_len > 65535:
            raise Exception("Message too long")
        if payload_len >= 126:
            header += bytes([
                (payload_len >> 8) & 0xff,
                payload_len & 0xff
            ])
        if self.send_mask:
            making_key = hashlib.sha1(payload).digest()[0:4]
            header += making_key
            payload_bin = self.apply_mask(payload_bin, making_key)

        self.socket.send(header + payload_bin)

    def receive_http_request(self):
        while b"\r\n\r\n" not in self.input_buffer:
            self.request()
        request_b, _ = self.input_buffer.split(b"\r\n\r\n", 1)
        self.input_buffer = self.input_buffer[len(request_b) + 4 :]
        request = str(request_b, "utf-8")
        lines = request.replace("\r", "").split("\n")
        method, uri, _ = lines[0].split(" ", 2)
        headers = {
            line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip()
            for line in lines[1:]
        }
        return method, uri, headers

    def send_websocket_handshake(self, req_headers):
        ws_key = req_headers["Sec-WebSocket-Key"]
        ws_accept = base64.b64encode(hashlib.sha1(bytes(ws_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11", "utf-8")).digest())
        reply = f"""HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-Websocket-Accept: {str(ws_accept, "utf-8")}

""".replace("\n", "\r\n")
        self.socket.sendall(bytes(reply, "utf-8"))


class ForwardingThread(threading.Thread):

    def __init__(self,
                 socket_src, fun_rcv,
                 socket_dest, fun_send,
                 tag=""):
        threading.Thread.__init__(self)
        self.socket_src = socket_src
        self.fun_rcv = fun_rcv
        self.socket_dest = socket_dest
        self.fun_send = fun_send
        self.tag = tag
        self.done = False

    def quit(self):
        self.done = True

    def run(self) -> None:

        while not self.done:
            try:
                msg = self.fun_rcv(self.socket_src)
                fb = FlatBuffer()
                fb.parse(msg, ThymioFB.SCHEMA)
                if fb.root.union_type not in {ThymioFB.MESSAGE_TYPE_PING}:
                    print("\n" + self.tag)
                    fb.dump()
                self.fun_send(self.socket_dest, msg)
            except TimeoutError:
                pass


class Proxy:

    TCP_PORT = 10000
    WS_PORT = 8597

    def __init__(self, tdm_addr=None, tdm_port=None, port=None, websocket=False):
        self.tdm_addr = tdm_addr
        self.tdm_port = tdm_port
        self.socket_tdm = None
        self.is_websocket = websocket

        self.port = port or Proxy.TCP_PORT
        self.socket_listener = None

    def start(self):
        self.stop()

        # connect to tdm
        self.socket_tdm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tdm.connect((self.tdm_addr, self.tdm_port))

        # start listening
        self.socket_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_listener.bind(('', self.port))
        self.socket_listener.listen(5)

    def accept(self):
        socket_client, address = self.socket_listener.accept()

        def read_uint32(socket) -> int:
            """Read an unsigned 32-bit number.
            """
            b = socket.recv(4)
            if len(b) < 4:
                raise TimeoutError()
            else:
                return b[0] + 256 * (b[1] + 256 * (b[2] + 256 * b[3]))

        def receive_msg_from_tcp(socket):
            """Read a complete message.
            """
            msg_len = read_uint32(socket)
            msg = socket.recv(msg_len)
            return msg

        def send_msg_to_tcp(socket, msg):
            """Send a message.
            """
            n = len(msg)
            blen = bytes([(n >> 8 * i) & 0xff for i in range(4)])
            socket.sendall(blen + msg)

        if self.is_websocket:
            ws = WebSocketState(socket_client)
            _, _, req_headers = ws.receive_http_request()
            if "Upgrade" not in req_headers or req_headers["Upgrade"] != "websocket":
                raise Exception("Unexpected http request")
            ws.send_websocket_handshake(req_headers)

            def receive_msg_from_ws(_):
                return ws.receive_packet()

            def send_msg_to_ws(_, msg):
                ws.send_packet(msg)

            thr = ForwardingThread(self.socket_tdm, receive_msg_from_tcp,
                                   None, send_msg_to_ws,
                                   tag="TDM ->")
            thr.start()
            thr = ForwardingThread(None, receive_msg_from_ws,
                                   self.socket_tdm, send_msg_to_tcp,
                                   tag="-> TDM")
            thr.start()
        else:
            thr = ForwardingThread(self.socket_tdm, receive_msg_from_tcp,
                                   socket_client, send_msg_to_tcp,
                                   tag="TDM ->")
            thr.start()
            thr = ForwardingThread(socket_client, receive_msg_from_tcp,
                                   self.socket_tdm, send_msg_to_tcp,
                                   tag="-> TDM")
            thr.start()

    def stop(self):
        if self.socket_tdm is not None:
            self.socket_tdm.close()
            self.socket_tdm = None
        if self.socket_listener is not None:
            self.socket_listener.close()
            self.socket_listener = None


if __name__ == "__main__":

    import getopt

    port = None
    is_ws = False
    debug = 0
    tdm_addr = "127.0.0.1"
    tdm_port = None

    def help():
        print(f"""Usage: python3 -m tdmclient.tools.proxy [options]
Run program on robot, from file or stdin

Options:
  --debug n    display diagnostic information (0=none, 1=basic, 2=more, 3=verbose)
  --help       display this help message and exit
  --port p     proxy port (default: {Proxy.TCP_PORT}, or {Proxy.WS_PORT} if --ws)
  --tdmaddr=H  tdm address (default: localhost)
  --tdmport=P  tdm port (no default)
  --ws         websocket instead of plain TCP
""")

    try:
        arguments, values = getopt.getopt(sys.argv[1:],
                                          "",
                                          [
                                              "debug=",
                                              "help",
                                              "port=",
                                              "tdmaddr=",
                                              "tdmport=",
                                              "ws",
                                          ])
    except getopt.error as err:
        print(str(err))
        sys.exit(1)
    for arg, val in arguments:
        if arg == "--help":
            help()
            sys.exit(0)
        elif arg == "--debug":
            debug = int(val)
        elif arg == "--port":
            port = int(val)
        elif arg == "--tdmaddr":
            tdm_addr = val
        elif arg == "--tdmport":
            tdm_port = int(val)
        elif arg == "--ws":
            is_ws = True
        else:
            print(f"Unknown option {arg}")
            sys.exit(1)
    if tdm_port is None:
        print("Missing --tdmport")
        sys.exit(1)

    if port is None:
        port = Proxy.WS_PORT if is_ws else Proxy.TCP_PORT

    proxy = Proxy(tdm_addr=tdm_addr, tdm_port=tdm_port, port=port, websocket=is_ws)
    proxy.start()
    while True:
        proxy.accept()
