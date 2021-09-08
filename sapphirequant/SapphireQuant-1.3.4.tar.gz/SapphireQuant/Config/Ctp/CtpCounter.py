from SapphireQuant.Config.Ctp.EnumServerType import EnumServerType


class CtpCounter:
    """
    CTP柜台信息
    """

    def __init__(self):
        self.quote_servers = []
        self.trade_servers = []

    def add(self, server):
        """
        添加服务器
        :param server:
        """
        if server.server_type == EnumServerType.quote:
            if self.quote_servers is None:
                self.quote_servers = [server]
            else:
                self.quote_servers.append(server)

        if server.server_type == EnumServerType.trade:
            if self.trade_servers is None:
                self.trade_servers = [server]
            else:
                self.trade_servers.append(server)

    def get_servers(self, server_type):
        """
        获取服务器
        :param server_type:
        :return:
        """
        if server_type == EnumServerType.quote:
            return self.quote_servers
        if server_type == EnumServerType.trade:
            return self.trade_servers
        return None
