from .base_stream_connector import BaseStreamConnector
from cnvrg.modules.errors import CnvrgError
try:
    import kafka
    imported = True
except ImportError:
    imported = False


class KafkaConnector(BaseStreamConnector):
    @staticmethod
    def key_type():
        return "kafka"

    def __init__(self, data_connector):
        if not imported: raise CnvrgError("Cannot find kafka-python module, please install it")
        super(KafkaConnector, self).__init__(data_connector)

    @staticmethod
    def requirements():
        return """kafka-python"""

    @property
    def __server(self):
        return "{host}:{port}".format(host=self.data.get("host"), port=(self.data.get("port") or "9092"))

    def producer(self):
        return kafka.KafkaProducer(bootstrap_servers=[self.__server], api_version=(0, 10))

    def consumer(self, *topics, **kwargs):
        return kafka.KafkaConsumer(*topics, bootstrap_servers=[self.__server], api_version=(0, 10), **kwargs)
