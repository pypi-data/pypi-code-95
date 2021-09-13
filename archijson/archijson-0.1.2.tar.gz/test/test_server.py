from archijson import ArchiServer
from sensitive_info import URL, TOKEN

server = ArchiServer(URL, TOKEN, 'engine')


def on_connect():
    print('exchanging')
    server.send('client', {'msg': 'hello'})


def on_receive(id, body):
    print(id)
    print(body)


server.on_connect = on_connect
server.on_receive = on_receive

# import socketio

# sio = socketio.Client()

# @sio.event
# def connect():
#     print('connection established')

# @sio.event
# def disconnect():
#     print('disconnected from server')

# sio.connect(URL)
# sio.wait()
