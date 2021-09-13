import socketio
import json


class ArchiServer:

    def __init__(self, URL, TOKEN, IDENTITY):
        self.URL = URL
        self.TOKEN = TOKEN
        self.IDENTITY = IDENTITY
        self.socket = self.setup()

    def setup(self):
        socket = socketio.Client(ssl_verify=False)

        @socket.event
        def connect():
            socket.emit('register', {
                        'token': self.TOKEN, 'identity': self.IDENTITY}, callback=self.__connect_callback)

        @socket.event
        def receive(ctx):
            if(type(ctx) == str):
                ctx = json.loads(ctx)
            id = ctx['id']
            body = ctx['body']

            self.on_receive(id, body)

        socket.connect(self.URL, transports='websocket')
        return socket

    def send(self, identity, body, id=None):
        # print('sending...')
        o = {'to': identity, 'body': body}
        if(id != None):
            o['id'] = id

        # print(o)
        self.socket.emit('exchange', o, callback=self.__print_status)

    def on_receive(self, id, body):
        pass

    def on_connect(self):
        pass

    def __connect_callback(self, o):
        self.__print_status(o)
        self.on_connect()

    def __print_status(self, o):
        print(o['status'])
