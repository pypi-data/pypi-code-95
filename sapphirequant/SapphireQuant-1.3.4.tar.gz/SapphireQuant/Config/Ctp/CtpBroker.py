from SapphireQuant.Config.Ctp.CtpCounterGroup import CtpCounterGroup


class CtpBroker:
    """
    期货Broker
    """
    def __init__(self, broker_id, name, default_group_name):
        self.id = broker_id
        self.name = name
        self.default_group_name = default_group_name
        self.ctp_counter_groups = []

    def add(self, server):
        """
        添加服务器
        :param server:
        """
        ctp_counter_group = None
        for data in self.ctp_counter_groups:
            if data.name == server.group_name:
                ctp_counter_group = data
                break
        if ctp_counter_group is None:
            ctp_counter_group = CtpCounterGroup(server.group_name)
            self.ctp_counter_groups.append(ctp_counter_group)
        ctp_counter_group.add(server)

    def get_servers_by_network_server_type(self, network_type, server_type):
        """
        获取服务器列表
        :param network_type:
        :param server_type:
        :return:
        """
        return self.get_servers(self.default_group_name, network_type, server_type)

    def get_servers(self, group_name, network_type, server_type):
        """
        获取服务器列表
        :param group_name:
        :param network_type:
        :param server_type:
        :return:
        """
        ctp_counter_group = None
        for data in self.ctp_counter_groups:
            if data.name == group_name:
                ctp_counter_group = data
                break
        if ctp_counter_group is not None:
            return ctp_counter_group.get_servers_by_network_server_type(network_type, server_type)

        print('未找到组名:{0}的服务器列表'.format(group_name))
        return None


