from functools import partial
from terality._terality.utils.config import TeralityConfig
from typing import Dict, Optional
from uuid import uuid4
import inspect

import pandas as pd

from common_client_scheduler import UploadRequest

from .. import upload_local_files, upload_s3_files, global_client
from ..awscredshelper import AwsCredentialsFetcher
from . import call_pandas_function
from ..utils.azure import parse_azure_filesystem, test_for_azure_libs


def _make_upload(path: str, storage_options: Optional[Dict] = None) -> UploadRequest:
    config = TeralityConfig.load(fallback_to_defaults=True)
    if config.skip_transfers:
        transfer_id = ""
        aws_region = None
    else:
        if path.startswith("s3://"):
            parts = path[len("s3://") :].split("/", 1)
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid S3 path, expected format: 's3://bucket/prefix' (prefix may be the empty string), got: '{path}'."
                )
            transfer_id = upload_s3_files(s3_bucket=parts[0], s3_key_prefix=parts[1])
            aws_region = global_client().get_upload_config().default_aws_region
        elif path.startswith("abfs://") or path.startswith("az://"):
            test_for_azure_libs()
            from ..data_transfers.azure import upload_azure_storage_files

            storage_account_name, container, folder = parse_azure_filesystem(path, storage_options)
            transfer_id = upload_azure_storage_files(storage_account_name, container, folder)
            aws_region = global_client().get_upload_config().default_aws_region
        else:
            transfer_id = str(uuid4())
            credentials_fetcher = AwsCredentialsFetcher()
            upload_local_files(path, transfer_id, credentials_fetcher.get_credentials())
            aws_region = None
    return UploadRequest(path=path, transfer_id=transfer_id, aws_region=aws_region)


def _treat_read_job(method_name, *args, **kwargs):
    """Special job to intercept file arguments and upload them to Terality for pd.read_xxx() jobs"""
    storage_options = kwargs.get("storage_options")
    if "path" in kwargs:
        kwargs["path"] = _make_upload(kwargs["path"], storage_options)
    else:
        path, *others = args
        args = [_make_upload(path, storage_options)] + others
    return call_pandas_function("free_function", None, method_name, *args, **kwargs)


# pandas top level functions (e.g defined as pd.SomeFunc) that Terality reimplements
_read_top_level_functions = {"read_parquet", "read_csv"}
# Even if for now the `read_xxx` function are the only one to be reimplemented by Terality,
# they have a very specific path in the code.
# Should we add any new top level function in the future, it can be implemented very differently
# than a "read_xxx" function.
# Make this clear by already having two concepts: generic "top level functions" whose only instances
# for now are the read functions.
top_level_functions = _read_top_level_functions


def get_dynamic_top_level_attribute(attribute: str):
    """Return the Terality or pandas module attribute with the given name.

    This function is intended to be the implementation of `__getattr__` (not `__getattribute__`) for the
    Terality module.

    When a user tries to access an attribute on the `terality` module that's not exported through the usual means,
    such as:

    >>> import terality as pd
    >>> df = pd.Something()

    then we use `_get_top_level_attribute` to dynamically resolve the `pd.Something` name.

    Note that data structures such as `pd.DataFrame` are exported in the `__init__` file of the Terality module
    and as such are never resolved through this function. Python only calls `__getattr__` when it can't resolve
    a name otherwise.

    The name resolution logic we use is:
    0. check that the pandas module defines the name. If not, raise an AttributeError
    1. intercept functions that need special client processing (such as read_csv, read_parquet...)
    2. if it's a class in pandas (`pd.Timestamp`), then return the pandas class
    3. if it's a module in pandas (`pd.tseries`), then return the pandas module
    4. otherwise, assume that it's a function, and send it to the Terality API

    In the future, we may implement an allowlist of functions to be locally executed by pandas (it could
    be sent by the server at session creation for instance).
    """
    # Check if the attribute is defined by the pandas library. If not, this line will raise an AttributeError.
    pd_attr = getattr(pd, attribute)

    # Special cases for NaT and NA
    if attribute == "NaT":
        return pd.NaT
    if attribute == "NA":
        return pd.NA

    # Intercept functions that need special handling (for now, only the "read_xxx" family of functions).
    if attribute in _read_top_level_functions:
        return partial(_treat_read_job, attribute)

    # Send class and module calls to the pandas module
    if inspect.isclass(pd_attr) or inspect.ismodule(pd_attr):
        return pd_attr

    # Send anything else to the Terality API
    return partial(call_pandas_function, "free_function", None, attribute)
