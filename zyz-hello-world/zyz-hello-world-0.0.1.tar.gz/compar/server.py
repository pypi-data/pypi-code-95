#!/usr/bin/env python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 60011))

while True:
    data, address = sock.recvfrom(1024)
    print('收到来自 {}:{} 的消息'.format(address[0], address[1]))
    print(data.decode('utf-8'))
