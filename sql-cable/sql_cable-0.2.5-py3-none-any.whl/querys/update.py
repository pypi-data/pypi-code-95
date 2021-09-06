import sqlite3


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
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # print(self.query)
        c.execute(self.query[:-5], self.params)
        conn.commit()
        conn.close()
        self.model_in.load_querrys(self.model_in)


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
        self.query = f"UPDATE {self.table_name} SET "
        self.params = []
        for column in kwargs:
            self.query += f"{column} = ?, "
            self.params.append(kwargs[column])
        self.query = self.query[:len(self.query) - 2]
        return Where(self.model_in, self.table_name, self.db_path, self.query, self.params)
