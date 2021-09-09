import os

from typing import Dict
from google.cloud import storage
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.helpers.apis_helper import download_file
from cnvrg.modules.storage.base_storage import BaseStorage


class GCPStorage(BaseStorage):
    def __init__(self, element: CnvrgFiles, working_dir: str, storage_resp: Dict):
        super().__init__(element, working_dir, storage_resp.get("sts"))

        try:
            os.remove(self.sts_local_file)
        except Exception:
            pass

        del storage_resp["sts"]

        self.key_file = os.path.join(os.path.expanduser("~"), ".cnvrg", ".gcp_cred.json")

        props = self.decrypt_dict(storage_resp, keys=["credentials"])

        download_file(props["credentials"], self.key_file)

        self.client = self._get_client()
        self.bucket = self.client.bucket("cnvrg-storage")

    def upload_single_file(self, file, target):
        try:
            bucket = self.bucket
            blob = bucket.blob(target)
            blob.upload_from_filename(file)
        except Exception as e:
            print(e)

    def download_single_file(self, file, target):
        pass

    def _get_client(self):
        return storage.Client.from_service_account_json(self.key_file)
