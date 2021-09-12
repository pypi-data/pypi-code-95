from ..base_client import BaseClient
from ..models.miner.extended_stats import ExtendedStats
from ..models.miner.stats import Stats


class Miner(object):
    def __init__(self, client: BaseClient):
        self._base_client = client
        self._miner_name = client.miner_name
        self._ip = client.ip
        self._port = int(client.port)
        self._method = client.method
        self._dual_mining_mode = client.dual_mining_mode
        self._setMethods()

    def get_stats(self) -> Stats:
        response = self._base_client.request(method=self.__basic_miner_state_method)
        self._base_client.check_response(response, f'Failed to get Statistic, {self._miner_name}.')
        result = Stats.from_json(response)
        return result

    def get_extended_stats(self) -> Stats:
        response = self._base_client.request(method=self.__extended_miner_state_method)
        self._base_client.check_response(response, f'Failed to get Statistic, {self._miner_name}.')
        result = ExtendedStats.from_json(response)
        return result

    def _setMethods(self):
        self.__basic_miner_state_method = 'miner_getstat1'
        self.__extended_miner_state_method = 'miner_getstat2'
        self.__miner_restart_method = 'miner_restart'
        self.__miner_reboot_method = 'miner_reboot'
        self.__control_gpu_method = 'control_gpu'
