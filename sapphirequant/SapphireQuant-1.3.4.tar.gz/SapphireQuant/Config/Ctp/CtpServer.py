from SapphireQuant.Config.Ctp.EnumNetworkType import EnumNetworkType


class CtpServer:
    """
    Ctp服务器信息
    """

    def __init__(self, address, group_name, server_type, network_type=EnumNetworkType.telecom):
        self.address = address
        self.group_name = group_name
        self.server_type = server_type
        self.network_type = network_type
