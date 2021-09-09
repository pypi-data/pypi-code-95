from ..base_connector import BaseConnector

class BaseSqlConnector(BaseConnector):

    def _connection(self):
        raise Exception("Not Implemented")

    def _cursor_default_options(self):
        return {}

    def cursor(self):
        return self._connection().cursor(**self._cursor_default_options())

    def run(self, sql):
        with self.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()