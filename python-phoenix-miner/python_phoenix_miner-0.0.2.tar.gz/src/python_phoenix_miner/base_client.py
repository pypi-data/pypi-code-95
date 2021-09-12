import json
import socket
from typing import Dict


class BaseClient(object):

    def __init__(self, miner_name, ip, port, dual_mining_mode=False, method="miner_getstat1"):
        self._miner_name = miner_name
        self._ip = ip
        self._port = int(port)
        self._method = method
        self._dual_mining_mode = dual_mining_mode

    @property
    def miner_name(self) -> str:
        return self._miner_name

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def method(self) -> str:
        return self._method

    @property
    def dual_mining_mode(self) -> bool:
        return self._dual_mining_mode

    def default_request(self) -> Dict[str, any]:
        message = {
                "id": 0,
                "jsonrpc": "2.0",
                "method": self.method
            }
        return message

    def request(self, method: str=None, **kwargs):
        default_request = self.default_request()
        json_data = {}
        if method:
            default_request["method"] = method
        data_bytes = json.dumps(default_request).encode('ascii')

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._ip, self._port))

            s.sendall(data_bytes)
            s.sendall(b'\n')
            data = s.recv(1024)
            s.close()
            print(f'Received {len(data)} byte(s)')
            json_data = json.loads(data)
        except Exception:
            print(f'Failed to connect to {self._ip}:{self._port}')
        return json_data

    def check_response(self, response, main_message: str):
        if 'id' not in response or 'jsonrpc' not in response or 'result' not in response:
            message = main_message + '\n'
            print(message)
