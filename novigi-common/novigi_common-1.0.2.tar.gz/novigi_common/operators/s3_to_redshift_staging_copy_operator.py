from typing import List, Optional, Union

from airflow.models.baseoperator import BaseOperator

from airflow.utils.decorators import apply_defaults

#from airflow.providers.postgres.hooks.postgres import PostgresHook
from novigi_common.hooks.postgres_hook import PostgresHook
from novigi_common.hooks.datalake_s3_hook import DataLakeS3Hook

class S3toRedshiftStagingOperator(BaseOperator):
    """

    """

    @apply_defaults
    def __init__(
        self,
        *,
        schema: str,
        table: str,
        report_name: str,
        datalake_s3_conn_id: str = 'datalake_s3_connection_default',
        redshift_conn_id: str = 'redshift_postgres_default',
        verify: Optional[Union[bool, str]] = None,
        copy_options: Optional[List] = None,
        autocommit: bool = False,
        truncate_table: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.schema = schema
        self.table = table
        self.report_name = report_name
        self.datalake_s3_conn_id = datalake_s3_conn_id
        self.redshift_conn_id = redshift_conn_id
        self.verify = verify
        self.copy_options = copy_options or []
        self.autocommit = autocommit
        self.truncate_table = truncate_table

    def execute(self, context) -> None:
        postgres_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        datalake_s3_hook = DataLakeS3Hook(datalake_s3_conn_id=self.datalake_s3_conn_id)
        s3_bucket = datalake_s3_hook.get_s3_bucket_name()
        iam_role = datalake_s3_hook.get_s3_iam_role()
        current_execution_date = context['execution_date'].strftime("%Y/%m/%d")
        s3_key = self.report_name + '/' + current_execution_date + '/' + self.report_name + '.csv'
        #s3_hook = S3Hook(aws_conn_id=self.aws_conn_id, verify=self.verify)
        #credentials = s3_hook.get_credentials()
        copy_options = '\n\t\t\t'.join(self.copy_options)

        copy_statement = f"""
            COPY {self.schema}.{self.table}
            FROM 's3://{s3_bucket}/{s3_key}'
            iam_role '{iam_role}'
            {copy_options};
        """

        if self.truncate_table:
            truncate_statement = f'TRUNCATE TABLE {self.schema}.{self.table};'
            sql = f"""
            BEGIN;
            {truncate_statement}
            {copy_statement}
            COMMIT
            """
        else:
            sql = copy_statement

        self.log.info('Executing COPY command...')
        postgres_hook.run(sql, self.autocommit)
        self.log.info("COPY command complete...")
