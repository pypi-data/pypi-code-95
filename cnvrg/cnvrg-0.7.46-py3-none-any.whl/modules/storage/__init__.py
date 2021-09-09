import os

from cnvrg.modules.storage.storage import Storage
from cnvrg.modules.storage.s3.storage import S3Storage
from cnvrg.modules.storage.azure.storage import AzureStorage
from cnvrg.modules.storage.minio.storage import MinioStorage
from cnvrg.modules.storage.gcp.storage import GCPStorage
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.helpers.apis_helper import get as apis_get

STORAGE_TYPE_GCP = "gcp"
STORAGE_TYPE_AZURE = "azure"
STORAGE_TYPE_S3 = "s3"
STORAGE_TYPE_MINIO = "minio"


def storage_factory(element: CnvrgFiles, working_dir=None):
    storage_resp = apis_get(element.get_storage_url()).get("client")
    working_dir = working_dir or element.get_working_dir() or os.curdir

    if storage_resp is None:
        return None
    if storage_resp.get("storage") == STORAGE_TYPE_S3:
        return S3Storage(element, working_dir, storage_resp)
    if storage_resp.get("storage") == STORAGE_TYPE_MINIO:
        return MinioStorage(element, working_dir, storage_resp)
    if storage_resp.get("storage") == STORAGE_TYPE_AZURE:
        return AzureStorage(element, working_dir, storage_resp)
    if storage_resp.get("storage") == STORAGE_TYPE_GCP:
        return GCPStorage(element, working_dir, storage_resp)
