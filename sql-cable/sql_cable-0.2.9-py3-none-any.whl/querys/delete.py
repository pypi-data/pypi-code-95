import sqlite3


class DeleteObject:
    def __init__(self, query, params):
        self.query = query
        self.params = params

    def add_query(self, c):
        c.execute(self.query, tuple(self.params))


class Delete:
    def __init__(self, table_name, db_path):
        self.table_name = table_name
        self.db_path = db_path

    def remove(self, separator="AND", **kwargs):
        query = f"DELETE FROM {self.table_name} WHERE "
        params = []
        for column in kwargs:
            query += f"{column} = ? AND "
            params.append(kwargs[column])
        if kwargs != {}:
            query = query[:-5]
        return DeleteObject(query, params)
