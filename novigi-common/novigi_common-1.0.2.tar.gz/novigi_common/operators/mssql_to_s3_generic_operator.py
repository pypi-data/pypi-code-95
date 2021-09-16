from typing import List, Optional, Union

from airflow.models.baseoperator import BaseOperator

from airflow.utils.decorators import apply_defaults

from novigi_common.hooks.odbc_hook import OdbcHook
from novigi_common.hooks.datalake_s3_hook import DataLakeS3Hook

class MssqlToS3GenericOperator(BaseOperator):
    """
    This operator is to handle generic sql queries
    """

    template_fields = ("query",)

    @apply_defaults
    def __init__(
        self,
        *,
        query: str,
        report_name: str,
        datalake_s3_conn_id: str = 'datalake_s3_connection_default',
        odbc_conn_id: str = 'mssql_default',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.query = query
        self.report_name = report_name
        self.datalake_s3_conn_id = datalake_s3_conn_id
        self.odbc_conn_id = odbc_conn_id


    def execute(self, context) -> None:
        odbc_hook = OdbcHook(odbc_conn_id=self.odbc_conn_id)
        datalake_s3_hook = DataLakeS3Hook(datalake_s3_conn_id=self.datalake_s3_conn_id)
        s3_bucket = datalake_s3_hook.get_s3_bucket_name()
        #iam_role = datalake_s3_hook.get_s3_iam_role()
        current_execution_date = context['execution_date'].strftime("%Y/%m/%d")
        s3_key = self.report_name + '/' + current_execution_date + '/' + self.report_name + '.csv'

        sql_query = self.query

        self.log.info('Prepared query: ' + sql_query)
        self.log.info('S3 key: ' + s3_key)

        data_frame = odbc_hook.get_pandas_df(sql_query)

        self.log.info("Fetch query complete...")

        s3_path = f's3://{s3_bucket}/{s3_key}'

        self.log.info("S3 Path " + s3_path)

        data_frame.to_csv(s3_path, index = False)

        self.log.info("S3 CSV creation complete...")
