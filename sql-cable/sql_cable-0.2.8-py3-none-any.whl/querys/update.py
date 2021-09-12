import sqlite3


class UpdateObject:
    def __init__(self, query, params):
        self.query = query
        self.params = params

    def add_query(self, c):
        c.execute(self.query, self.params)


class Where:
    def __init__(self, model_in, table_name, db_path, query, params):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.query = query
        self.params = params

    def where(self, **kwargs):
        self.query += " WHERE "
        for column in kwargs:
            self.query += f"{column} = ? AND "
            self.params.append(kwargs[column])
        return UpdateObject(self.query[:-5], self.params)


class Update:
    def __init__(self, model_in, table_name, db_path):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.get_columns()

    def get_columns(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({self.table_name});")
        table_data = c.fetchall()
        self.columns = []
        for column in table_data:
            self.columns.append(column[1])

    def set(self, separator='AND', **kwargs):
        query = f"UPDATE {self.table_name} SET "
        params = []
        for column in kwargs:
            query += f"{column} = ?, "
            params.append(kwargs[column])
        query = query[:len(query) - 2]
        return Where(self.model_in, self.table_name, self.db_path, query, params)
