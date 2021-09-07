from setup_demo import rpc_func
import traceback
import socketserver
from setup_demo.Serializer import Serializer
import logging
from uuid import uuid4, UUID

HOST, PORT = "0.0.0.0", 8000
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', level=logging.DEBUG)
uuid = lambda: str(uuid4())


def is_valid_uuid(s):
    try:
        UUID(s)
        return True
    except:
        return False


def try_except(func):
    def inner(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return 0, ret
        except:
            print(traceback.format_exc())
            return -1, traceback.format_exc()

    return inner


@try_except
def exec_func(func_name, args=[], kwargs={}, obj=rpc_func):
    func = getattr(obj, func_name)
    ret = func(*args, **kwargs)
    return ret


class RPCHandler(socketserver.BaseRequestHandler):
    instance_map = {}

    def handle(self) -> None:
        conn = self.request
        logging.info('client connected')
        conn.sendall('connect success'.encode())
        while True:
            data = conn.recv(2048)
            if data == b"":
                logging.info('client disconnected')
                break
            func_name, args, kwargs, instance_id = Serializer.get_func_info(data)
            if is_valid_uuid(instance_id):
                try:
                    instance = RPCHandler.instance_map[instance_id]
                except KeyError as err:
                    code, ret = -1, err.with_traceback()
                    ret_info = {"code": code, "result": ret}
                    conn.send(Serializer.serialize(ret_info))
                    break
            else:
                instance = rpc_func

            code, ret = self.exec_func(func_name, args, kwargs, instance)

            if code == 0:
                if isinstance(ret, (int, str, list, tuple, dict)):
                    ret_info = {"code": code, "result": ret}
                else:
                    instance_id = uuid()
                    RPCHandler.instance_map[instance_id] = ret
                    ret_info = {"code": code, "result": instance_id}
            else:
                ret_info = {"code": code, "reason": ret}
            conn.send(Serializer.serialize(ret_info))

    @try_except
    def exec_func(self, func_name, args=[], kwargs={}, obj=rpc_func):
        func = getattr(obj, func_name)
        ret = func(*args, **kwargs)
        return ret


def main():
    server = socketserver.ThreadingTCPServer((HOST, PORT), RPCHandler)
    logging.info('server started')
    logging.info('listening at {0}:{1}'.format(HOST, PORT))
    server.serve_forever()


if __name__ == "__main__":
    main()
