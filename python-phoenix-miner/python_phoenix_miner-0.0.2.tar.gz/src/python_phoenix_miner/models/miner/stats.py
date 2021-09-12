import json

from typing import Dict


class Stats(object):

    def __init__(
            self, miner_version=None, running_time=None, eth_hash_rate=None, eth_hash_rate_by_gpu=None,
            dcr_hash_rate_by_gpu=None, eth_accepted_shares=None, eth_rejected_shares=None, dcr_hash_rate=None,
            dcr_accepted_shares=None, dcr_rejected_shares=None, gpu_temp_list=None, gpu_fan_list=None, mining_pool=None,
            eth_invalid_shares=None, eth_pool_switches=None, dcr_invalid_shares=None, dcr_pool_switches=None
    ):
        """

        :param miner_version: miner version and the currently mined coin (if known)
        :param running_time:
        :param eth_hash_rate:
        :param eth_hash_rate_by_gpu:
        :param dcr_hash_rate_by_gpu:
        :param eth_accepted_shares:
        :param eth_rejected_shares:
        :param dcr_hash_rate:
        :param dcr_accepted_shares:
        :param dcr_rejected_shares:
        :param gpu_temp_list:
        :param gpu_fan_list:
        :param mining_pool:
        :param eth_invalid_shares:
        :param eth_pool_switches:
        :param dcr_invalid_shares:
        :param dcr_pool_switches:
        """
        self._miner_version = miner_version
        self._running_time = running_time
        self._eth_hash_rate = eth_hash_rate
        self._eth_hash_rate_by_gpu = eth_hash_rate_by_gpu
        self._dcr_hash_rate_by_gpu = dcr_hash_rate_by_gpu
        self._eth_accepted_shares = eth_accepted_shares
        self._eth_rejected_shares = eth_rejected_shares
        self._dcr_hash_rate = dcr_hash_rate
        self._dcr_accepted_shares = dcr_accepted_shares
        self._dcr_rejected_shares = dcr_rejected_shares
        self._gpu_temp_list = gpu_temp_list
        self._gpu_fan_list = gpu_fan_list
        self._mining_pool = mining_pool
        self._eth_invalid_shares = eth_invalid_shares
        self._eth_pool_switches = eth_pool_switches
        self._dcr_invalid_shares = dcr_invalid_shares
        self._dcr_pool_switches = dcr_pool_switches

    @property
    def miner_version(self) -> str:
        """miner version and the currently mined coin (if known)"""
        return self._miner_version

    @miner_version.setter
    def miner_version(self, value: str):
        self._miner_version = value

    @property
    def running_time(self) -> int:
        """running time, in minutes"""
        return self._running_time

    @running_time.setter
    def running_time(self, value: int):
        self._running_time = value

    @property
    def eth_hash_rate(self) -> int:
        """total ethash hashrate in kH/s"""
        return self._eth_hash_rate

    @eth_hash_rate.setter
    def eth_hash_rate(self, value: int):
        self._eth_hash_rate = value

    @property
    def eth_hash_rate_by_gpu(self) -> list:
        """ethash hashrate for each GPU in kH/s"""
        return self._eth_hash_rate_by_gpu

    @eth_hash_rate_by_gpu.setter
    def eth_hash_rate_by_gpu(self, value: list):
        self._eth_hash_rate_by_gpu = value

    @property
    def dcr_hash_rate_by_gpu(self) -> list:
        """
        secondary coin hashrate for each GPU in kH/s (or off if dual mining is not used)
        """
        return self._dcr_hash_rate_by_gpu

    @dcr_hash_rate_by_gpu.setter
    def dcr_hash_rate_by_gpu(self, value: list):
        self._dcr_hash_rate_by_gpu = value

    @property
    def eth_accepted_shares(self) -> int:
        """number of ethash shares"""
        return self._eth_accepted_shares

    @eth_accepted_shares.setter
    def eth_accepted_shares(self, value: int):
        self._eth_accepted_shares = value

    @property
    def eth_rejected_shares(self) -> int:
        """number of ethash rejected shares"""
        return self._eth_rejected_shares

    @eth_rejected_shares.setter
    def eth_rejected_shares(self, value: int):
        self._eth_rejected_shares = value

    @property
    def dcr_hash_rate(self) -> int:
        """total secondary coin hashrate in kH/s"""
        return self._dcr_hash_rate

    @dcr_hash_rate.setter
    def dcr_hash_rate(self, value: int):
        self._dcr_hash_rate = value

    @property
    def dcr_accepted_shares(self) -> int:
        """number of secondary coin shares"""
        return self._dcr_accepted_shares

    @dcr_accepted_shares.setter
    def dcr_accepted_shares(self, value: int):
        self._dcr_accepted_shares = value

    @property
    def dcr_rejected_shares(self) -> int:
        """number of secondary coin rejected shares"""
        return self._dcr_rejected_shares

    @dcr_rejected_shares.setter
    def dcr_rejected_shares(self, value: int):
        self._dcr_rejected_shares = value

    @property
    def gpu_temp_list(self) -> list:
        """temperature for each GPU"""
        return self._gpu_temp_list

    @gpu_temp_list.setter
    def gpu_temp_list(self, value: list):
        self._gpu_temp_list = value

    @property
    def gpu_fan_list(self) -> list:
        """fan speed in % for each GPU"""
        return self._gpu_fan_list

    @gpu_fan_list.setter
    def gpu_fan_list(self, value: list):
        self._gpu_fan_list = value

    @property
    def mining_pool(self) -> str:
        """current mining pool. When using dual mode, the second pool will be listed too. The name of the pool may be prefixed by >, which indicates that the connection to the pool is down (e.g. during the initial pool connection, or if the miner is paused for more than a few minutes, and it disconnects from the pool until the mining is resumed)"""
        return self._mining_pool

    @mining_pool.setter
    def mining_pool(self, value: str):
        self._mining_pool = value

    @property
    def eth_invalid_shares(self) -> list:
        """number of ethash invalid shares"""
        return self._eth_invalid_shares

    @eth_invalid_shares.setter
    def eth_invalid_shares(self, value: str):
        self._eth_invalid_shares = value

    @property
    def eth_pool_switches(self) -> list:
        """number of ethash pool switches"""
        return self._eth_pool_switches

    @eth_pool_switches.setter
    def eth_pool_switches(self, value: str):
        self._eth_pool_switches = value

    @property
    def dcr_invalid_shares(self) -> list:
        """number of secondary coin invalid shares"""
        return self._dcr_invalid_shares

    @dcr_invalid_shares.setter
    def dcr_invalid_shares(self, value: str):
        self._dcr_invalid_shares = value

    @property
    def dcr_pool_switches(self) -> list:
        """number of secondary coin pool switches"""
        return self._dcr_pool_switches

    @dcr_pool_switches.setter
    def dcr_pool_switches(self, value: str):
        self._dcr_pool_switches = value

    def to_json(self):
        return json.dumps(self.to_dictionary(), indent=4)

    def to_dictionary(self):
        result = {}
        # result["statistics"] = self.statistics
        # result["workers"] = self.workers
        # result["current_statistics"] = self.current_statistics
        # result["settings"] = self.settings
        return result

    @staticmethod
    def from_json(content: Dict):
        result = Stats()
        data = content.get("result", {})
        if len(data) > 8:
            result.miner_version = data[0]
            result.running_time = int(data[1])

            eth_hash_stat_list = data[2].split(";")
            result.eth_hash_rate = int(eth_hash_stat_list[0])
            result.eth_accepted_shares = int(eth_hash_stat_list[1])
            result.eth_rejected_shares = int(eth_hash_stat_list[2])

            result.eth_hash_rate_by_gpu = []
            for mhs in data[3].split(";"):
                if mhs != "off":
                    result.eth_hash_rate_by_gpu.append(int(mhs))
                else:
                    result.eth_hash_rate_by_gpu.append(mhs)

            dcr_hash_stat_list = data[4].split(";")
            result.dcr_hash_rate = int(dcr_hash_stat_list[0])
            result.dcr_accepted_shares = int(dcr_hash_stat_list[1])
            result.dcr_rejected_shares = int(dcr_hash_stat_list[2])

            result.dcr_hash_rate_by_gpu = []
            for mhs in data[5].split(";"):
                if mhs != "off":
                    result.dcr_hash_rate_by_gpu.append(int(mhs))
                else:
                    result.dcr_hash_rate_by_gpu.append(mhs)

            # Temperature and Fan speed(%) pairs for all GPUs.
            result.gpu_temp_list = []
            result.gpu_fan_list = []
            _raw_temp_and_fan = data[6].split(";")
            for i in range(0, len(_raw_temp_and_fan), 2):
                result.gpu_temp_list.append(int(_raw_temp_and_fan[i]))
                result.gpu_fan_list.append(int(_raw_temp_and_fan[i + 1]))

        result.mining_pool = data[7]
        dcr_and_eth_share_stats = data[8].split(";")
        result.eth_invalid_shares = dcr_and_eth_share_stats[0]
        result.eth_pool_switches = dcr_and_eth_share_stats[1]
        result.dcr_invalid_shares = dcr_and_eth_share_stats[2]
        result.dcr_pool_switches = dcr_and_eth_share_stats[3]

        return result
