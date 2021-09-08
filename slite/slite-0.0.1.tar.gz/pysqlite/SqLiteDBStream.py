import sqlite3
import dbstream


class SqLiteDBStream(dbstream.DBStream):
    def __init__(self, db_path, client_id=None):
        super().__init__(instance_name="", client_id=client_id)
        self.db_path = db_path

    def connection(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _execute_query_custom(self, query):
        con = self.connection()
        cursor = con.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            cursor.close()
            con.close()
            raise e
        con.commit()
        result = cursor.fetchall()
        cursor.close()
        con.close()
        if result:
            return [dict(r) for r in result]
