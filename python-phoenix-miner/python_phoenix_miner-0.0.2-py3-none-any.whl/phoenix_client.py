from .base_client import BaseClient
from .controllers.miner import Miner


class PhoenixClient:

    def __init__(self, miner_name, ip, port, dual_mining_mode=False, method='miner_getstat1'):
        self._base_client = BaseClient(miner_name, ip, port, dual_mining_mode, method)
        self._miner = Miner(self._base_client)

    @property
    def miner_name(self) -> str:
        return self._base_client.miner_name

    @property
    def ip(self) -> str:
        return self._base_client.ip

    @property
    def port(self) -> int:
        return self._base_client.port

    @property
    def dual_mining_mode(self) -> bool:
        return self._base_client.dual_mining_mode

    @property
    def method(self) -> str:
        return self._base_client.method

    @property
    def base_client(self) -> BaseClient:
        return self._base_client

    @property
    def Miner(self) -> Miner:
        return self._miner
