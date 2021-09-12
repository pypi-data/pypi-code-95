from .base_sql_connector import BaseSqlConnector
from cnvrg.modules.errors import CnvrgError
is_loaded = False
try:
    import thrift_sasl
    from pyhive import hive
    is_loaded = True

except ImportError:
    is_loaded = False


class HiveConnector(BaseSqlConnector):

    @staticmethod
    def requirements():
        return """thrift_sasl\npyhive\nthrift"""


    @staticmethod
    def key_type():
        return "hive"

    def __init__(self, data_connector):
        if not is_loaded: raise CnvrgError("Cant find pyhive module, please install it before using HiveConnector")
        super(HiveConnector, self).__init__(data_connector)

    def _connection(self):
        # host=None, port=None, username=None, database='default', auth=None,
        #                  configuration=None, kerberos_service_name=None, password=None,
        #                  thrift_transport=None
        return hive.Connection(**self.data)
