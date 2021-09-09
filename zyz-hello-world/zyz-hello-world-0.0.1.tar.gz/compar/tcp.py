#!/usr/bin/env python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('www.baidu.com', 80))
sock.send(b'GET / HTTP/1.1\r\nHOST: www.baidu.com\r\nConnection:close\r\n\r\n')
buffer = []

while True:
    content = sock.recv(1024)
    if content:
        buffer.append(content)
    else:
        break

web_content = b''.join(buffer)
print(web_content)

http_header, http_content = web_content.split(b'\r\n\r\n',1)
with open('baidu.html', 'wb') as f:
    f.write(http_content)