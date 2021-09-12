from .base_sql_connector import BaseSqlConnector
from cnvrg.modules.errors import CnvrgError
try:
    import snowflake
    import snowflake.connector
    imported = True
except ImportError:
    imported = False



class SnowflakeConnector(BaseSqlConnector):

    @staticmethod
    def key_type():
        return "snowflake"

    @staticmethod
    def requirements():
        return """snowflake"""

    def __init__(self, data_connector):
        if not imported: raise CnvrgError("Cant find module snowflakes")
        super(SnowflakeConnector, self).__init__(data_connector)

    def _connection(self):
        return snowflake.connector.connect(**self.data)