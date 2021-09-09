import os
import boto3

from typing import Dict
from cnvrg.modules.storage.base_storage import BaseStorage
from cnvrg.modules.cnvrg_files import CnvrgFiles
from boto3.s3.transfer import TransferConfig


config = TransferConfig(
    multipart_threshold=1024 * 25,
    max_concurrency=10,
    multipart_chunksize=1024 * 25,
    use_threads=True
)


class S3Storage(BaseStorage):
    def __init__(self, element: CnvrgFiles, working_dir: str, storage_resp: Dict):
        super().__init__(element, working_dir, storage_resp.get("path_sts"))

        try:
            os.remove(self.sts_local_file)
        except Exception:
            pass

        del storage_resp["path_sts"]

        props = self.decrypt_dict(storage_resp, keys=["sts_a", "sts_s", "sts_st", "bucket", "region"])

        self.s3props = {
            "aws_access_key_id": props.get("sts_a"),
            "aws_secret_access_key": props.get("sts_s"),
            "aws_session_token": props.get("sts_st"),
            "region_name": props.get("region")
        }
        self.bucket = props.get("bucket")
        self.region = props.get("region")
        self.client = self._get_client()

    def upload_single_file(self, file, target):
        try:
            self.client.upload_file(file, self.bucket, target, Config=config)
        except Exception as e:
            print(e)

    def download_single_file(self, file, target):
        pass
        # try:
        #     self.client.download_file(self.bucket, file, target, Config=config)
        # except Exception as e:
        #     print(e)

    def _get_client(self):
        return boto3.client('s3', **self.s3props)
