#!/usr/bin/env python
import socket
import threading

def echo_server(client: socket.socket, address: tuple):
    print('欢迎来自{}:{}的新客户端'.format(address[0], address[1]))
    client.send('Welcome from{}:{}'.format(address[0], address[1]).encode('utf-8'))
    while True:
        data = client.recv(1024)
        if data == b'exit':
            break
        elif data:
            print(data.decode('utf-8'))
        else:
            break
    print('客户端推出了！')
    client.close()

#创建socket对象实例，采用IPV4和TCP协议
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 2018))
server.listen(5)
print('Server start! Listening 127.0.0.1:2018')

while True:
    client, address = server.accept()
    t = threading.Thread(target=echo_server, args=[client, address])
    t.start()
    # echo_server(client, address)