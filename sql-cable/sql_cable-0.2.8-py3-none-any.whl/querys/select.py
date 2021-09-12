import sqlite3
import math


def get_data(db_path, querys, fetch, params=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if params:
        c.execute(querys, tuple(params))
    else:
        c.execute(querys)
    if fetch == 'all':
        result = c.fetchall()
    else:
        result = c.fetchone()
    return result


class ForeignRowObject:
    def __init__(self, rows, value):
        self.rows = rows
        self.value = value


class RowObject:
    def __init__(self, row_data, columns):
        self.row_data = row_data
        self.columns = columns
        self.row_to_var()

    def row_to_var(self):
        for i in range(len(self.columns)):
            if self.columns[list(self.columns.keys())[i]].fk:
                foreign_model = self.columns[list(self.columns.keys())[i]].foreign_model
                foreign_pk = foreign_model.primary_key(foreign_model)
                _locals = locals()
                exec(f"foreign_data = foreign_model.select.filter({foreign_pk}={self.row_data[i]}).all()", globals(), _locals)
                exec(f"self.{list(self.columns.keys())[i]} = value", {'self': self, 'value': ForeignRowObject(_locals['foreign_data'], self.row_data[i])})

            else:
                exec(f"self.{list(self.columns.keys())[i]} = value", {'self': self, 'value': self.row_data[i]})


class PaginationPage:
    def __init__(self, model_in, table_name, db_path, columns, query, params, per_page, page_num):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params
        self.per_page = per_page
        self.page_num = page_num
        self.get_all_data()
        self.get_items()

    def get_all_data(self):
        result = get_data(self.db_path, self.query, 'all', params=self.params)
        self.page_amount = math.ceil(len(result) / self.per_page)

    def get_items(self):
        start = self.per_page * (self.page_num - 1)
        self.query = self.query + " LIMIT ? OFFSET ?"
        self.params.append(self.per_page)
        self.params.append(start)
        items = get_data(self.db_path, self.query, 'all', self.params)
        f_result = []
        if items != []:
            for row in items:
                f_result.append(RowObject(row, self.columns))
            self.items = f_result

    def iter_page(self, first, last, left, right):
        self.page_nums = []
        self.page_nums.append(1)
        for i in range(left):
            if self.page_num - (i + 1) > 1:
                self.page_nums.append(self.page_num - (i + 1))
        if self.page_num != 1 and self.page_num != self.page_amount:
            self.page_nums.append(self.page_num)
        for i in range(right):
            if self.page_num + (i + 1) < self.page_amount:
                self.page_nums.append(self.page_num + (i + 1))
        if self.page_amount != 1:
            self.page_nums.append(self.page_amount)
        return self.page_nums


class f_funcs:
    def __init__(self, model_in, table_name, db_path, columns, query, params):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params

    def all(self):
        result = get_data(self.db_path, self.query, 'all', params=self.params)
        f_result = []
        if result != []:
            for row in result:
                f_result.append(RowObject(row, self.columns))
            return f_result

    def one(self):
        # print(self.query)
        result = get_data(self.db_path, self.query, 'one', params=self.params)
        if result:
            return RowObject(result, self.columns)

    def paginate(self, per_page, page_num):
        return PaginationPage(self.model_in, self.table_name, self.db_path, self.columns, self.query, self.params, per_page, page_num)


class Sort_by(f_funcs):
    def __init__(self, model_in, table_name, db_path, columns, query, params):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params

    def sort_by(self, conjunctive_op='AND', **args):
        if 'pre_data' in list(args.keys()):
            args = args['pre_data']
        for arg in args:
            self.query += f" ORDER BY {arg} {args[arg]} {conjunctive_op} "
        return f_funcs(self.model_in, self.table_name, self.db_path, self.columns, self.query[:-5], self.params)


class Filter:
    def __init__(self, model_in, table_name, db_path, columns, query, params):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params

    def filter(self, conjunctive_op='AND', **args):
        self.query += " WHERE "
        self.params = []
        if 'pre_data' in list(args.keys()):
            args = args['pre_data']
        for param in args:
            self.query += f"{param} = ? {conjunctive_op} "
            self.params.append(args[param])
        return Sort_by(self.model_in, self.table_name, self.db_path, self.columns, self.query[:-5], self.params)


class Get(f_funcs):
    def __init__(self, model_in, table_name, db_path, columns):
        self.model_in = model_in
        self.table_name = table_name
        self.db_path = db_path
        self.columns_unsorted = columns
        self.get_columns()
        self.query = f"SELECT * FROM {self.table_name}"
        self.params = []

    def get_columns(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({self.table_name});")
        table_data = c.fetchall()
        self.columns = {}
        for column in table_data:
            for col in self.columns_unsorted:
                if self.columns_unsorted[col].name == column[1]:
                    self.columns[column[1]] = self.columns_unsorted[col]

    def filter(self, conjunctive_op='AND', **kwargs):
        return Filter(self.model_in, self.table_name, self.db_path, self.columns, self.query, self.params).filter(conjunctive_op=conjunctive_op, pre_data=kwargs)

    def sort_by(self, conjunctive_op='AND', **kwargs):
        return Sort_by(self.model_in, self.table_name, self.db_path, self.columns, self.query, self.params).sort_by(conjunctive_op=conjunctive_op, pre_data=kwargs)
