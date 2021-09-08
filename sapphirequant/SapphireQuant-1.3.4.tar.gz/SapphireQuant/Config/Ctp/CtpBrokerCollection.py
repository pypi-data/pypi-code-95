
class CtpBrokerCollection:
    """
    期货Broker集合
    """
    def __init__(self):
        self.default_broker_id = ''
        self.brokers = []

    def add(self, broker):
        """
        添加broker
        :param broker:
        :return:
        """
        for data in self.brokers:
            if data.id == broker.id:
                return

        self.brokers.append(broker)

    def get_broker(self, broker_id):
        """
        获取broker
        :param broker_id:
        :return:
        """
        for broker in self.brokers:
            if broker.id == broker_id:
                return broker

    def get_servers(self, broker_id, group_name, network_type, server_type):
        """
        获取服务器组
        :param broker_id:
        :param group_name:
        :param network_type:
        :param server_type:
        :return:
        """
        broker = self.get_broker(broker_id)
        if broker is not None:
            return broker.get_servers(group_name, network_type, server_type)

        return []

    def get_servers_by_network_server_type(self, network_type, server_type):
        """
        获取服务器组
        :param network_type:
        :param server_type:
        :return:
        """
        broker = self.get_broker(self.default_broker_id)
        if broker is not None:
            return broker.get_servers(network_type, server_type)

        return []

    def get_broker_ids(self):
        """
        获取broker_id
        :return:
        """
        lst_broker_id = []
        for broker in self.brokers:
            lst_broker_id.append(broker.id)
        return lst_broker_id
