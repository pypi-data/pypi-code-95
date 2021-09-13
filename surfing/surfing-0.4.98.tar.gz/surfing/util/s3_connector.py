import boto3
import sys
import pandas
sys.path.append('/Users/cjiang/Documents/GitHub/surfing/python/')
from surfing.util.singleton import Singleton
from surfing.util.config import SurfingConfigurator


class S3Connector(metaclass=Singleton):

    def __init__(self, config_path=None) -> None:
        if config_path:
            self.settings = SurfingConfigurator(config_path).get_aws_settings()
        else:
            self.settings = SurfingConfigurator().get_aws_settings()

    def get_conn(self):
        return boto3.resource(
            's3',
            region_name=self.settings.region_name,
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
        )

    def get_client(self):
        return boto3.client(
            's3',
            region_name=self.settings.region_name,
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
        )


    def put_obj(self, obj, bucket, key):
        client = self.get_client()
        client.put_object(Body=obj, Bucket=bucket, Key=key)

    def get_obj(self, bucket, key):
        client = self.get_client()
        obj = client.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read()

    def put_df(self, df, bucket, key):
        path = f's3://{bucket}/{key}'
        df.to_feather(path)

    def get_df(self, bucket, key):
        path = f's3://{bucket}/{key}'
        return pandas.read_feather(path)

    def put_private_obj(self, obj, key):
        self.put_obj(obj, self.settings.research_private_bucket, key)

    def put_public_obj(self, obj, key):
        self.put_obj(obj, self.settings.research_public_bucket, key)

    def get_private_obj(self, key):
        return self.get_obj(self.settings.research_private_bucket, key)

    def get_public_obj(self, key):
        return self.get_obj(self.settings.research_public_bucket, key)

    def put_public_df(self, df, key):
        self.put_df(df, self.settings.research_public_bucket, key)

    def put_private_df(self, df, key):
        self.put_df(df, self.settings.research_private_bucket, key)

    def get_public_df(self, key):
        return self.get_df(self.settings.research_public_bucket, key)

    def get_private_df(self, key):
        return self.get_df(self.settings.research_private_bucket, key)

    # ----------
    def upload_public_file(self, file_path, file_key):
        s3 = self.get_conn()
        s3.meta.client.upload_file(file_path, self.settings.research_public_bucket, file_key, ExtraArgs={'ContentType': 'text/plain'})

'''
buckets = s3_client.list_buckets()
for bucket in buckets['Buckets']:
    print(bucket['CreationDate'].ctime(), bucket['Name'])
'''

if __name__ == '__main__':
    print(SurfingConfigurator('../../../etc/config.json').get_aws_settings())
    s3 = S3Connector().get_conn()
    s3_client = S3Connector().get_client()
    to_insert = b'this is a test'
    S3Connector().put_private_obj(to_insert, 'test1.txt')
    a = S3Connector().get_private_obj('test1.txt')
    print(type(a), a)
