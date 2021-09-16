from typing import List, Optional, Union

from airflow.models.baseoperator import BaseOperator

from airflow.utils.decorators import apply_defaults

from novigi_common.hooks.odbc_hook import OdbcHook
from novigi_common.hooks.datalake_s3_hook import DataLakeS3Hook

class MssqlToS3Operator(BaseOperator):
    """

    """

    @apply_defaults
    def __init__(
        self,
        *,
        schema: str = 'dbo',
        table: str,
        report_name: str,
        datalake_s3_conn_id: str = 'datalake_s3_connection_default',
        odbc_conn_id: str = 'mssql_default',
        field_list: Optional[List] = None,
        last_update_field: str = 'last_update',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.schema = schema
        self.table = table
        self.report_name = report_name
        self.datalake_s3_conn_id = datalake_s3_conn_id
        self.odbc_conn_id = odbc_conn_id
        self.field_list = field_list or []
        self.last_update_field = last_update_field


    def execute(self, context) -> None:
        odbc_hook = OdbcHook(odbc_conn_id=self.odbc_conn_id)
        datalake_s3_hook = DataLakeS3Hook(datalake_s3_conn_id=self.datalake_s3_conn_id)
        s3_bucket = datalake_s3_hook.get_s3_bucket_name()
        #iam_role = datalake_s3_hook.get_s3_iam_role()
        current_execution_date = context['execution_date'].strftime("%Y/%m/%d")
        s3_key = self.report_name + '/' + current_execution_date + '/' + self.report_name + '.csv'

        query_start_date = context['execution_date'].strftime("%Y-%m-%d")
        query_end_date = context['execution_date'].strftime("%Y-%m-%d")

        if context['dag_run'].conf is not None:
            query_start_date = context['dag_run'].conf.get('start_date', None) or context['execution_date'].strftime("%Y-%m-%d")
            query_end_date = context['dag_run'].conf.get('end_date', None) or context['execution_date'].strftime("%Y-%m-%d")

        filter_string = '*'
        if len(self.field_list) > 0:
            self.log.info("Filtering the columns "+ str(self.field_list))
            filter_string = ','.join(self.field_list)

        sql_query = f'SELECT {filter_string} FROM [{self.schema}].[{self.table}] WHERE {self.last_update_field} BETWEEN \'{query_start_date} 00:00:00\' AND \'{query_end_date} 23:59:59\''

        self.log.info('Prepared query: ' + sql_query)
        self.log.info('S3 key: ' + s3_key)

        data_frame = odbc_hook.get_pandas_df(sql_query)

        self.log.info("Fetch query complete...")

        s3_path = f's3://{s3_bucket}/{s3_key}'

        self.log.info("S3 Path " + s3_path)

        data_frame.to_csv(s3_path, index = False)

        self.log.info("S3 CSV creation complete...")
