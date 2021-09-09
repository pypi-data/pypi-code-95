import os
import boto3
import urllib3

from typing import Dict
from boto3.s3.transfer import TransferConfig
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.modules.storage.base_storage import BaseStorage
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = TransferConfig(
    multipart_threshold=1024 * 25,
    max_concurrency=10,
    multipart_chunksize=1024 * 25,
    use_threads=True
)


class MinioStorage(BaseStorage):
    def __init__(self, element: CnvrgFiles, working_dir: str, storage_resp: Dict):
        super().__init__(element, working_dir, storage_resp.get("path_sts"))

        try:
            os.remove(self.sts_local_file)
        except Exception:
            pass

        del storage_resp["path_sts"]

        props = self.decrypt_dict(storage_resp, keys=["sts_a", "sts_s", "sts_st", "bucket", "region", "endpoint"])

        self.s3props = {
            "endpoint_url": props.get("endpoint"),
            "aws_access_key_id": props.get("sts_a"),
            "aws_secret_access_key": props.get("sts_s"),
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

    def _get_client(self):
        return boto3.client('s3', verify=False, **self.s3props)
