import socket
from setup_demo.Serializer import Serializer
from time import time, sleep
import subprocess
from sys import executable as pyexe

time_millis = lambda :time() * 1000
HOST, PORT = "127.0.0.1", 8000


def constract_data(func_name, args=[], kwargs={}):
    return {"functionName": func_name,
            "args": args,
            "kwargs": kwargs
            }


class RPCSocketClient:

    def __init__(self, url, port):
        self.client = socket.socket()
        self.server_host = (url, port)
        self._connect_()

    def _connect_(self):
        self.client.connect(self.server_host)
        _ = self.client.recv(128)

    def __getattr__(self, item):
        if item in dir(self):
            return self.__dict__(item)

        def func(*args, **kwargs):
            return self._exec_(item, args, kwargs)

        return func

    def _func_(self, *args, **kwargs):
        return self._exec_(self.func_name, args=args, kwargs=kwargs)

    def _exec_(self, func_name, args=[], kwargs={}):
        data = constract_data(func_name, args, kwargs)
        self.client.send(Serializer.serialize(data))
        ret_info = Serializer.deserialize(self.client.recv(512))
        if ret_info['code'] == 0:
            return ret_info['result']
        else:
            raise Exception(ret_info['reason'])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.send(b'')


class RPCClass(RPCSocketClient):

    def __init__(self, url, port, class_name):
        super().__init__(url, port)
        self.instance_id = None
        self.instance_init(class_name)

    def instance_init(self, class_name, args=[], kwargs={}):
        data = constract_data(class_name, args, kwargs)
        self.client.send(Serializer.serialize(data))
        ret_info = Serializer.deserialize(self.client.recv(2048))
        if ret_info.get("code") == 0:
            self.instance_id = ret_info.get("result")
        else:
            raise Exception(ret_info['reason'])

    def _exec_(self, func_name, args=[], kwargs={}):
        data = {
             "functionName": func_name,
             "args": args,
             "kwargs": kwargs,
             "instanceID": self.instance_id
        }
        self.client.send(Serializer.serialize(data))
        ret_info = Serializer.deserialize(self.client.recv(512))
        if ret_info['code'] == 0:
            return ret_info['result']
        else:
            raise Exception(ret_info['reason'])


def wait_server_started(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((host, port))
            print("server is started")
            break
        except Exception as err:
            print("server is not started")
        sleep(3)

    s.close()


def main():
    try:
        # p = subprocess.Popen("{0} rpc_server.py".format(pyexe))
        p = subprocess.Popen("{0} -m setup_demo.rpc_server".format(pyexe))
        wait_server_started(HOST, PORT)
        with RPCClass(HOST, PORT, "demo") as client:
            t = time_millis()
            for i in range(3):
                ret1 = client.test()
                ret2 = client.get_id()
                print(ret2)
            print(time_millis() - t)
    finally:
        p.terminate()
        ...

if __name__ == "__main__":
    main()


