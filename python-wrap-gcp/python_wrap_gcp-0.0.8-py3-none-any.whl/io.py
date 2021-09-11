from google.cloud import storage
import re, os, pickle, json
from python_wrap_gcp.docs.config import FROM_LOCAL, TO_LOCAL, GCPConfig


def get_gcs_blob(path, account_json_path=None):
    if account_json_path is None:  # assume from a VM
        storage_client = storage.Client()
    else:
        storage_client = storage.Client.from_service_account_json(account_json_path)
    bucket_name = re.findall("//(.+?)/", path)[0]
    file_name = '/'.join(path.split('/')[3:])
    blob = storage_client.get_bucket(bucket_name).blob(file_name)
    return blob


def emulate_open(path, account_json_path=None, from_local=FROM_LOCAL,
                 to_local=TO_LOCAL, method='rb', data=None):
    """
    Provide an abstract API to read/write data either locally or to a GCP bucket
    :param path:
    :param account_json_path: str, GCP access key local path
    :param from_local: bool, load requested file from local driver
    :param to_local: bool, write data locally
    :param method: str, similar to build-in python function `open`
        `rb`: read binary
        `wb`: write binary
    :param data: object, file to save
    :return: None
    """
    if method == 'rb':
        if from_local:
            return open(path, method).read()
        blob = get_gcs_blob(path, account_json_path=account_json_path)
        return blob.download_as_bytes()

    if method == 'wb':
        if data is None:
            raise AssertionError("data not provided")
    local_file_name = path if to_local else path.split('/')[-1]
    if path.endswith('.pkl') or path.endswith('.pickle'):
        pickle.dump(data, open(local_file_name, 'wb+'))
    if path.endswith('.json'):
        json.dump(data, open(local_file_name, 'w+'))
    if path.endswith('.prq') or path.endswith('.parquet'):
        data.to_parquet(path)
        return
    if to_local:
        return
    blob = get_gcs_blob(path, account_json_path=account_json_path)
    blob.upload_from_filename(local_file_name)
    os.remove(local_file_name)


def emulate_ls(path, from_local=FROM_LOCAL):
    """
    Provide an abstract API to list files either locally or from the GCP bucket
    :param path: str
    :param from_local: bool
    :param account_json_path: str, local path
    :return: list
    """
    if from_local:
        return os.listdir(path)
    else:
        storage_client = storage.Client()
        return [blob.name for blob in storage_client.list_blobs(GCPConfig.BUCKET, prefix=path)]


def get_blob_update_date(name):
    """
    Retrieve GCP blob update time
    :param name: str, path to file on GCP, without bucket name
    :return: datetime
    """
    storage_client = storage.Client()
    try:
        blob = next(iter((storage_client.list_blobs(GCPConfig.BUCKET, prefix=name))))
    except StopIteration:
        raise AssertionError(f"`{name}` does not exist")
    return blob.updated


# TODO: re/load logic here
