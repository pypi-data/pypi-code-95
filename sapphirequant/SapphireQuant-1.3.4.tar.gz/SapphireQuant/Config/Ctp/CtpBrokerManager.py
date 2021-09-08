from SapphireQuant.Config.Ctp.CtpBrokerCollection import CtpBrokerCollection


class CtpBrokerManager:
    """
    CtpBroker管理器
    """
    def __init__(self):
        self.ctp_broker_collection = CtpBrokerCollection()

    def load(self, config_path):
        """
        加载
        :param config_path:
        """
        pass

    def get_servers(self, broker_id, group_name, network_type, server_type):
        """

        :param broker_id:
        :param group_name:
        :param network_type:
        :param server_type:
        :return:
        """
        return self.ctp_broker_collection.get_servers(broker_id, group_name, network_type, server_type)

    def get_servers_by_broker_id_network_server_type(self, broker_id, network_type, server_type):
        """

        :param broker_id:
        :param network_type:
        :param server_type:
        :return:
        """
        return self.ctp_broker_collection.get_servers(broker_id, network_type, server_type)

    def get_servers_by_network_server_type(self, network_type, server_type):
        """

        :param network_type:
        :param server_type:
        :return:
        """
        return self.ctp_broker_collection.get_servers(network_type, server_type)

    def get_broker(self, broker_id):
        """

        :param broker_id:
        :return:
        """
        return self.ctp_broker_collection.get_broker(broker_id)

    def get_broker_ids(self):
        """

        :return:
        """
        return self.ctp_broker_collection.get_broker_ids()