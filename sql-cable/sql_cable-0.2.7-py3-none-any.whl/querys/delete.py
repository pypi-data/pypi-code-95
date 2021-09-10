import sqlite3


class Delete:
    def __init__(self, model_in, table_name, db_path):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path

    def remove(self, separator="AND", **kwargs):
        query = f"DELETE FROM {self.table_name} WHERE "
        params = []
        for column in kwargs:
            query += f"{column} = ? AND "
            params.append(kwargs[column])
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query[:-5], tuple(params))
        conn.commit()
        conn.close()
        self.model_in.load_querrys(self.model_in)
