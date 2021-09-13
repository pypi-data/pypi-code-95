import logging
from csv import reader
from contextlib import closing

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
from airflow.hooks.base_hook import BaseHook

class NovigiCSVToDatabaseExportOperator(BaseOperator):

        template_fields = ['data_file']

        ALLOWED_CONN_TYPE = {
                    "jdbc",
                    "mssql",
                    "mysql",
                    "odbc",
                    "oracle",
                    "postgres"
        }

        def __init__(self, table, data_file, conn_id, operation="INSERT INTO", csv_has_headers=True, column_dict = None, database = None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.conn_id = conn_id
            self.operation = operation
            self.table = table
            self.data_file = data_file
            self.column_dict = column_dict
            self.csv_has_headers = csv_has_headers
            self.database = database
            self.hook = None

        def get_hook(self):
            conn = BaseHook.get_connection(self.conn_id)

            if conn.conn_type not in self.ALLOWED_CONN_TYPE:
                raise AirflowException(
                        "Invalid connection type. Supported connection types: {}".format(list(self.ALLOWED_CONN_TYPE))
                )

            if not self.hook:
                self.hook = conn.get_hook()
                if self.database:
                    self.hook.schema = self.database

            return self.hook

        def form_insert_query(self, operation, table, columns, row):
            if isinstance(columns, dict):
                column_keys = columns.keys()
            else:
                column_keys = columns

            questions = ','.join(['%s' for item in column_keys])
            if not self.csv_has_headers and self.column_dict is None:
                return """{} {} VALUES ({});""".format(operation, table, questions)
            else:
                column_names = ','.join(column_keys)
                return """{} {} ({}) VALUES ({});""".format(operation, table, column_names, questions)

        def execute(self, context):
            hook = self.get_hook()
            hook.set_autocommit(conn=hook.get_conn(), autocommit=False)
            logging.info("Importing CSV data to SQL. CSV: {}".format(self.data_file))
            conn = hook.get_conn()
            with closing(conn.cursor()) as cursor:
                with open(self.data_file,"r") as infile:
                    csv_reader = reader(infile)
                    if not self.column_dict and self.csv_has_headers:
                        self.column_dict = {k: v for v, k in enumerate(next(csv_reader))}
                    if self.csv_has_headers:
                        next(csv_reader, None)
                    for row in csv_reader:
                        sql_statement = self.form_insert_query(self.operation, self.table, self.column_dict, row)
                        if not self.column_dict:
                            cursor.execute(sql_statement, tuple(None if x == '' else str(x) for x in row))
                        else:
                            cursor.execute(sql_statement, tuple(None if x == '' else str(x) for x in list(map(lambda n: row[n], self.column_dict.values()))))

            conn.commit()

            logging.info("Completed Novigi CSV to Database operator. CSV: {}".format(self.data_file))
            return True