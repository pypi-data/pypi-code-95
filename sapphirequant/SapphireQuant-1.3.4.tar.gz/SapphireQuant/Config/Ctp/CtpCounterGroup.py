from SapphireQuant.Config.Ctp.CtpCounter import CtpCounter
from SapphireQuant.Config.Ctp.EnumNetworkType import EnumNetworkType


class CtpCounterGroup:
    """
    Ctp柜台组
    """

    def __init__(self, name):
        self.name = name
        self.telecom_counter = None
        self.unicom_counter = None

    def add(self, server):
        """
        添加服务器
        :param server:
        """
        if server.network_type == EnumNetworkType.telecom:
            if self.telecom_counter is None:
                self.telecom_counter = CtpCounter()
                self.telecom_counter.add(server)
        if server.network_type == EnumNetworkType.unicom:
            if self.unicom_counter is None:
                self.unicom_counter = CtpCounter()
                self.unicom_counter.add(server)

    def get_counter(self, network_type):
        """
        获取柜台
        :param network_type:
        :return:
        """
        if network_type == EnumNetworkType.telecom:
            return self.telecom_counter
        if network_type == EnumNetworkType.unicom:
            return self.unicom_counter
        return None

    def get_servers(self, network_type, server_type):
        """
        获取服务器
        :param network_type:
        :param server_type:
        :return:
        """
        if network_type == EnumNetworkType.telecom:
            return self.telecom_counter.get_servers(network_type, server_type)
        if network_type == EnumNetworkType.unicom:
            return self.unicom_counter.get_servers(network_type, server_type)
        return None
