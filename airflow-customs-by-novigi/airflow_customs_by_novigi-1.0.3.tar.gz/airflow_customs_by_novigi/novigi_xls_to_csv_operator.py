import logging
import csv
from contextlib import closing
import xlrd
# install modules
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
from airflow.hooks.base_hook import BaseHook

class NovigiXlsToCSVOperator(BaseOperator):

    def __init__(self, input_excel: str, output_csv: str, sheet_name: str = None, column_range: range = None, row_range: range = None, headers: list = None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.input_excel = input_excel
            self.output_csv = output_csv
            self.sheet_name = sheet_name
            self.column_range = column_range
            self.row_range = row_range
            self.headers = headers

    def clean(self, value):
            #use this callback to clean
            return value

    def execute(self, context):
            logging.info("Exporting EXCEL data to csv: {} -> CSV: {}".format(self.input_excel, self.output_csv))

            wb = xlrd.open_workbook(filename = self.input_excel)
            if self.sheet_name is None:
                sheet = wb.sheet_by_index(0)
            else:
                sheet = wb.sheet_by_name(self.sheet_name)

            if self.column_range is None:
                self.column_range = range(sheet.ncols)

            if self.row_range is None:
                self.row_range = range(sheet.nrows)

            with open(self.output_csv, "w") as outfile:
                writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
                if self.headers is not None:
                    writer.writerow(headers)

                for i in self.row_range:
                    row = []
                    for j in self.column_range:
                        cell = sheet.cell_value(i, j)
                        row.append(cell)

                    writer.writerow([self.clean(x) for x in row])

            logging.info("Completed Novigi XLS to CSV operator. CSV: {}".format(self.output_csv))

            return True
