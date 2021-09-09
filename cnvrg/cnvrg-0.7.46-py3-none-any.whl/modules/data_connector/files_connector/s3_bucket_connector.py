from .base_files_connector import BaseFileConnector
import cnvrg.modules.errors as errors
import os
import os

is_loaded = False
try:
    import boto3
    is_loaded = True

except ImportError:
    is_loaded = False



class S3BucketConnector(BaseFileConnector):

    @staticmethod
    def key_type():
        return "s3_bucket"

    @staticmethod
    def client(**data):
        return boto3.client('s3', aws_access_key_id=data.get("key"), aws_secret_access_key=data.get("secret"),
                            aws_session_token=data.get("session_token"), region_name=data.get("region"))

    @staticmethod
    def session(**data):
        return boto3.Session(aws_access_key_id=data.get("key"), aws_secret_access_key=data.get("secret"),
                             aws_session_token=data.get("session_token"), region_name=data.get("region"))

    @staticmethod
    def bucket(bucket=None, **data):
        return S3BucketConnector.session(**data).resource('s3').Bucket(bucket)

    def __init__(self, data_connector, prefix=None, working_dir=None):
        super(S3BucketConnector, self).__init__(data_connector)
        self.client = None
        self.__files = []
        self.__prefix = prefix or self.data.get("prefix")
        temp_working_dir = working_dir or "/data"
        if not os.access(temp_working_dir, os.W_OK): temp_working_dir = os.path.expanduser("~/cnvrg_datasets")
        self.__working_dir = os.path.join(temp_working_dir, self._data_connector)
        os.makedirs(self.__working_dir, exist_ok=True)
        self.__connect(**self.data)

    def __connect(self, access_key_id=None, secret_access_key=None, session_token=None, region=None, bucket=None, **kwargs):
        if not is_loaded: raise errors.CnvrgError("Cant load boto3 library.")
        self.data = {"aws_access_key_id": access_key_id, "aws_secret_access_key": secret_access_key, "aws_session_token": session_token, "region_name": region, "bucket": bucket}


    def get_bucket(self):
        return S3BucketConnector.bucket(**self.data)

    def get_client(self):
        return S3BucketConnector.client(**self.data)

    @property
    def working_dir(self):
        return self.__working_dir

    def list_files(self, prefix=None):
        if len(self.__files) == 0: self.__list_files(prefix=prefix)
        return self.__files

    def get_file(self, s3_path):
        local_path = os.path.join(self.__working_dir, s3_path)
        return self.__download_file(s3_path, local_path)

    def __len__(self):
        if len(self.__files) == 0: self.__list_files()
        return len(self.__files)

    def __getitem__(self, item):
        storage_path = self.__files[item]
        return self.get_file(storage_path)

    def __download_file(self, storage_path, local_path):
        client = S3BucketConnector.client(**self.data)
        if os.path.exists(local_path):
            return local_path
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        client.download_file(self.data.get("bucket"), storage_path, local_path)
        return local_path

    def __list_files(self, prefix=None):
        self.__files = []
        prefix = prefix or self.__prefix
        for o in self.get_bucket().objects.filter(Prefix=prefix or ''):
            self.__files.append(o.key)

        ### we need the have a callback to let the user
        ### sort the files.
        return self._files_callback(self.__files)
