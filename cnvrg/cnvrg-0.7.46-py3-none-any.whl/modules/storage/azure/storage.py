import os

from typing import Dict
from azure.storage.blob import BlobServiceClient
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.modules.storage.base_storage import BaseStorage


class AzureStorage(BaseStorage):
    def __init__(self, element: CnvrgFiles, working_dir: str, storage_resp: Dict):
        super().__init__(element, working_dir, storage_resp.get("sts"))

        try:
            os.remove(self.sts_local_file)
        except Exception:
            pass

        del storage_resp["sts"]

        props = self.decrypt_dict(storage_resp, keys=["container", "storage_access_key", "storage_account_name", "container"])
        account_name = props["storage_account_name"]
        accout_key = props["storage_access_key"]
        container = props["container"]

        self.access_key = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net".format(account_name, accout_key)
        self.container_name = container
        self.service = self._get_service()

    def upload_single_file(self, file, target):
        try:
            client = self.service.get_blob_client(self.container_name, blob=target)
            with open(file, "rb") as data:
                client.upload_blob(data, overwrite=True)
        except Exception as e:
            print(e)

    def download_single_file(self, file, target):
        pass

    def _get_service(self):
        return BlobServiceClient.from_connection_string(self.access_key)
