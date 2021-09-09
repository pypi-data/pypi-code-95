#!/usr/bin/env python
import socket

#创建socket对象实例，采用IPV4和TCP协议
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 2018))

for i in range(100):
    client.send('Hello World!'.encode('utf-8'))
    reply = client.recv(1024)
    print(reply.decode('utf-8'))

client.send(b'exit')
client.close()