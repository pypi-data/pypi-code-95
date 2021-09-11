import inspect, pickle, json, re
import pandas as pd
from python_wrap_gcp.misc.helpers import log
from python_wrap_gcp.io import get_blob_update_date, emulate_open
from python_wrap_gcp.docs.config import GCPConfig


def get_abs_path_prefix(blob):
    """
    Transform absolute GCP path with bucket name into relative path, compatible to prefix filtering
    :param blob: str, path, absolute or relative
    :return: str, relative GCP path
    """
    fake_delimiter = '$%^&||'
    bucket_name = next(iter(re.findall(r"//(.+?)/", blob)), fake_delimiter)
    prefix = blob.split(bucket_name)[-1]
    if prefix[0] == '/':
        prefix = prefix[1:]
    return prefix


def load_gcs_file(blob, fmt=None, **kwargs):
    """
    Load GCP blob (file) name with one of supported Python formats: pickle, parquet, json
    :param blob: str, blob name
    :param fmt: str, in case blob name doesn't end with file format
    :return: tuple:
        data: requested file
        data_last_seen: datetime, the latest time blob has been updated
    """
    if blob.endswith(".prq") or blob.endswith('.parquet') or fmt == 'parquet':
        data = pd.read_parquet(blob)
    else:
        as_str = emulate_open(blob, method='rb', from_local=False)
        if blob.endswith(".pkl") or blob.endswith('.pickle') or fmt == 'pickle':
            data = pickle.loads(as_str)
        elif blob.endswith(".json") or fmt == 'json':
            data = json.loads(as_str)
        else:
            raise ValueError("data format not understood")
    blob_prefix = get_abs_path_prefix(blob)
    data_last_seen = get_blob_update_date(blob_prefix).replace(microsecond=0)
    return data, data_last_seen


def reload(blob, last_time_seen, **kwargs):
    """
    Reload a file from Google Cloud Storage upon file update
    :param blob: str, name of blob together with bucket, ie. gs://bucket-name/data-folder/file.pkl
    :param last_time_seen: datetime, time when the last time data seen
    :return: False or tuple:
        data, the last time data seen
    """
    blob_prefix = get_abs_path_prefix(blob)
    blob_last_time_seen = get_blob_update_date(blob_prefix)
    if (blob_last_time_seen - last_time_seen).total_seconds() > GCPConfig.SECONDS_THRESHOLD:
        log(inspect.stack(),
            f"data change detected. Current: {last_time_seen}; available: {blob_last_time_seen}", "I")
        data, last_time_seen = load_gcs_file(blob, **kwargs)
        log(inspect.stack(), f"data reloaded", "I")
        return data, last_time_seen
    return False
