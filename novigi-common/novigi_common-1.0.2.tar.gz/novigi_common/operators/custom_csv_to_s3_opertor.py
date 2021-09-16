from airflow.models.baseoperator import BaseOperator

from airflow.utils.decorators import apply_defaults

from datetime import datetime
import csv
import logging
import pandas as pd
import datetime
import os


class CustomCSVToS3Operator(BaseOperator):

    template_fields = ("query","inputCSVPath")

    @apply_defaults
    def __init__(
        self,
        inputCSVPath: str,
        outputCSVDir: str,
        reportName: str,
        encoding: str = "cp1252",
        filterOutColumns=None,
        query: str = None,
        dateColumns=None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.filterOutColumns = (
            filterOutColumns or []
        )  # columns which are needed to filterout from the source CSV
        self.inputCSVPath = inputCSVPath  # source file path
        self.outputCSVDir = outputCSVDir  # file output path
        self.reportName = reportName
        self.encoding = encoding          # encoding type
        self.csvFileName = reportName + ".csv"
        self.query = query  # query to filterout rows from csv based on conditions. ex : ('Salary_in_1000 >= 100 & Age < 60 ')
        self.dateColumns = dateColumns or []

    def stringToDate(self, inputDate):
        for fmt in ("%d/%m/%Y %H:%M:%S %p", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(inputDate, fmt)
            except:
                continue
        return datetime.datetime(2050, 12, 31)

    def execute(self, context):
        current_execution_date = context["execution_date"].strftime("%Y/%m/%d")
        fullCSVPath = os.path.join(
            self.outputCSVDir, self.reportName, current_execution_date, self.csvFileName
        )

        logging.info("Exporting data from " + self.inputCSVPath)
        data_frame = pd.read_csv(self.inputCSVPath, index_col=False, encoding= self.encoding )

        if len(self.dateColumns) > 0:
            logging.info("Formatting date columns " + str(self.dateColumns))
            for column in self.dateColumns:
                data_frame[column] = data_frame[column].apply(
                    lambda x: self.stringToDate(x)
                )

        if len(self.filterOutColumns) > 0:
            logging.info("Dropping the columns " + str(self.filterOutColumns))
            data_frame = data_frame.drop(self.filterOutColumns, axis=1)

        if self.query.strip():
            logging.info("Applying the query " + self.query)
            data_frame = data_frame.query(self.query)

        logging.info("Writing data into the " + fullCSVPath)
        data_frame.to_csv(fullCSVPath, index=False)

        logging.info("Copying CSV to S3 completed ")
        return True
