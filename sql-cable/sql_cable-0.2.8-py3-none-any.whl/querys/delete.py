import sqlite3


class DeleteObject:
    def __init__(self, query, params):
        self.query = query
        self.params = params

    def add_query(self, c):
        c.execute(self.query, tuple(self.params))


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
        return DeleteObject(query[:-5], params)
