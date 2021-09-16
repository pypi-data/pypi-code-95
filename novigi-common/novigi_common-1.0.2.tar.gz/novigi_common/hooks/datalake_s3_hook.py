from airflow.hooks.dbapi_hook import DbApiHook

'''
TODO: Further improve this Hook

Conn Id: datalake_s3_connection_default
Conn Type: S3
Extra: {"aws_s3_bucket_name":"_your_aws_bucket_name_", "aws_s3_iam_role": "_your_aws_s3_iam_role_"}
Leave all the other fields (Host, Schema, Login) blank.

'''

class DataLakeS3Hook(DbApiHook):

    conn_name_attr = 'datalake_s3_conn_id'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        conn_id = getattr(self, self.conn_name_attr)
        self.connection = self.get_connection(conn_id)

    def get_s3_bucket_name(self):
        return self.connection.extra_dejson['aws_s3_bucket_name']

    def get_s3_iam_role(self):
        return self.connection.extra_dejson['aws_s3_iam_role']
