# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing the implementation for a file based cache to be used for saving automl data between runs."""
from typing import Any, Callable, Dict, Iterable, Optional, Tuple
from collections import namedtuple
import logging
import os
import shutil

import numpy as np
import pandas as pd
from scipy import sparse

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.automl_error_definitions import CacheOperation, InsufficientMemory
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import CacheException, ResourceException

from azureml.automl.runtime.shared._parqueter import Parqueter
from azureml.automl.runtime.shared.cache_store import CacheStore

logger = logging.getLogger()

CachedValue = namedtuple("CachedValue", ["path", "func"])


class _CacheConstants:
    # default task timeout
    DEFAULT_TASK_TIMEOUT_SECONDS = 900

    class FileExtensions:
        # Extension name for files that are saved by Numpy.save()
        NUMPY_FILE_EXTENSION = "npy"

        # Extension name for files that are saved by SciPy.save()
        SCIPY_SPARSE_FILE_EXTENSION = "npz"

        # Extension name for files saved with Pickle.dumps()
        PICKLE_FILE_EXTENSION = "pkl"

        # Extension for numpy arrays stored in parquet format.
        NUMPY_PARQUET_FILE_EXTENSION = "npy.parquet"

        # Extension for numpy arrays that are single dimensional.
        NUMPY_SINGLE_DIM_FILE_EXTENSION = "npys.parquet"

        # Extension for pandas dataframes stored in parquet format.
        DF_PARQUET_FILE_EXTENSION = "df.parquet"

        # Extension for spmatrix stored in parquet format.
        SCIPY_SPARSE_PARQUET_FILE_EXTENSION = "spm.parquet"

        ALL = [
            DF_PARQUET_FILE_EXTENSION,
            NUMPY_FILE_EXTENSION,
            NUMPY_PARQUET_FILE_EXTENSION,
            NUMPY_SINGLE_DIM_FILE_EXTENSION,
            PICKLE_FILE_EXTENSION,
            SCIPY_SPARSE_FILE_EXTENSION,
            SCIPY_SPARSE_PARQUET_FILE_EXTENSION
        ]


class LazyFileCacheStore(CacheStore):
    """
    Cache store backed by the local file system.

    We consider this a "lazy" store as it doesn't pre-fetch the saved_as information.
    Instead we simply load the metadata and leverage the file extension to deserialize
    objects.
    """
    _pickler = DefaultPickler()

    _extension_to_deserializer = {
        _CacheConstants.FileExtensions.DF_PARQUET_FILE_EXTENSION: Parqueter.load_pandas_dataframe,
        _CacheConstants.FileExtensions.NUMPY_FILE_EXTENSION: np.load,
        _CacheConstants.FileExtensions.NUMPY_PARQUET_FILE_EXTENSION: Parqueter.load_numpy_array,
        _CacheConstants.FileExtensions.NUMPY_SINGLE_DIM_FILE_EXTENSION: Parqueter.load_single_dim_numpy_array,
        _CacheConstants.FileExtensions.PICKLE_FILE_EXTENSION: _pickler.load,
        _CacheConstants.FileExtensions.SCIPY_SPARSE_FILE_EXTENSION: sparse.load_npz,
    }

    def __init__(
        self,
        path: str,
    ):
        """
        File based cache store - constructor.

        :param path: store path
        """
        super(LazyFileCacheStore, self).__init__()

        self._root = os.path.join(path, "cache")
        self._init_cache_folder()

    def __getstate__(self):
        """
        Get this cache store's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        return super().__getstate__(), {
            "_root": self._root,
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        super_state, my_state = state
        self._root = my_state["_root"]
        super().__setstate__(super_state)

    def __repr__(self):
        return "{}(path=\"{}\")".\
            format(self.__class__.__name__, self._root[:self._root.rfind("cache") - 1])

    def _init_cache_folder(self) -> None:
        """
        Create temp dir.

        :return: temp location
        """
        try:
            os.makedirs(self._root, exist_ok=True)
        except OSError as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.error("Failed to initialize the cache store. Error code: {}".format(e.errno))
            raise CacheException._with_error(AzureMLError.create(
                CacheOperation, target="cache-init", operation_name="initialization",
                path=self._root, os_error_details=str(e)),
                inner_exception=e
            ) from e

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """
        Serialize the values and add them to cache and local file system.

        :param keys: store keys
        :param values: store values
        """
        with self.log_activity():
            for k, v in zip(keys, values):
                try:
                    logger.info("Uploading key: " + k)
                    self._write(k, v)
                except OSError as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    logger.error("Failed to persist the keys [{}] to the local disk. Error code: {}".format(
                        ",".join(keys), e.errno))
                    raise CacheException._with_error(
                        AzureMLError.create(CacheOperation, target="cache-add", operation_name="add",
                                            path=self._root, os_error_details=str(e)),
                        inner_exception=e
                    ) from e
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to add key {} to cache. Exception type: {}".format(k, e.__class__.__name__)
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def get(self, keys: Iterable[str], default: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get deserialized object from store.

        :param keys: store keys
        :param default: returns default value if not present
        :return: deserialized objects
        """
        res = dict()

        with self.log_activity():
            for key in keys:
                try:
                    logger.info("Getting data for key: " + key)
                    item = self.cache_items.get(key, None)
                    if item is not None:
                        obj = item.func(item.path)
                    elif default is not None:
                        obj = default
                    else:
                        raise RuntimeError("Key not found.")

                    res[key] = obj
                except OSError as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    logger.error("Failed to get the keys [{}] from the local cache on disk. Error code: {}".format(
                        ",".join(keys), e.errno))
                    raise CacheException._with_error(
                        AzureMLError.create(CacheOperation, target="cache-get", operation_name="get",
                                            path=self._root, os_error_details=str(e)),
                        inner_exception=e
                    ) from e
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to retrieve key {} from cache. Exception type: {}".format(
                        key, e.__class__.__name__)
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

        return res

    def set(self, key: str, value: Any) -> None:
        """
        Set to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key: str) -> None:
        """
        Remove key from store.

        :param key: store key
        """
        to_remove = self.cache_items[key]
        os.remove(os.path.join(self._root, to_remove.path))
        del self.cache_items[key]

    def remove_all(self) -> None:
        """Remove all the cache from store."""
        self.cache_items = {}
        shutil.rmtree(self._root)

    def load(self) -> None:
        """Load from store."""
        logger.info("Loading from file cache")
        with self.log_activity():
            files = os.listdir(self._root)
            for f in files:
                file, ext = self._split_file_ext(f)

                deserializer_func = LazyFileCacheStore._extension_to_deserializer.get(
                    ext, self._pickler.load
                )

                self.cache_items[file] = CachedValue(path=os.path.join(self._root, f), func=deserializer_func)

    def unload(self):
        """Unload from store."""
        self.remove_all()
        self._init_cache_folder()

    def _serialize_pandas_dataframe_as_parquet(self, file_name: str, obj: pd.DataFrame) -> str:
        """
        Serialize a pandas dataframe into a parquet file.

        :param file_name: File name to write to.
        :param obj: Pandas dataframe.
        :return:
        """
        Contract.assert_type(value=obj, name='obj', expected_types=pd.DataFrame, log_safe=True)
        path = os.path.join(self._root, file_name)
        return Parqueter.dump_pandas_dataframe(obj, path)

    def _serialize_numpy_ndarray_as_parquet(self, file_name: str, obj: np.ndarray) -> str:
        """
        Serialize numpy array into a parquet file.

        :param file_name: File name to write to.
        :param obj: Numpy object.
        :return:
        """
        Contract.assert_type(value=obj, name='obj', expected_types=np.ndarray, log_safe=True)
        path = os.path.join(self._root, file_name)
        return Parqueter.dump_numpy_array(obj, path)

    def _serialize_numpy_ndarray(self, file_name: str, obj: np.ndarray) -> str:
        Contract.assert_type(value=obj, name='obj', expected_types=np.ndarray)
        path = os.path.join(self._root, file_name)
        np.save(path, obj, allow_pickle=False)
        return path

    def _serialize_scipy_sparse_matrix(self, file_name: str, obj: Any) -> str:
        Contract.assert_true(sparse.issparse(obj), message='`obj` must be a sparse matrix.')
        path = os.path.join(self._root, file_name)
        sparse.save_npz(path, obj)
        return path

    def _serialize_object_as_pickle(self, file_name: str, obj: Any) -> str:
        path = os.path.join(self._root, file_name)
        self._pickler.dump(obj, path=path)
        return path

    def _get_deserializer_based_on_extension(self, extension: str) -> Callable[[str], Any]:
        """
        Get appropriate deserializer based on extension of the file. Default deserializer is the
        default pickler's load() method.

        :param extension: Extension of the file trying to be deserialized.
        :return: Callable deserializer method.
        """
        deserializer = self._extension_to_deserializer.get(extension, None)
        if deserializer is None:
            logger.info('Did not find deserializer for extension: {}. Falling back to pickler'
                        'to load the object'.format(extension))

        return deserializer or self._pickler.load

    def _serialize(self, file_name: str, obj: Any) -> CachedValue:
        if isinstance(obj, np.ndarray) and obj.dtype != np.object:
            if obj.ndim == 1:
                ext = _CacheConstants.FileExtensions.NUMPY_SINGLE_DIM_FILE_EXTENSION
            else:
                ext = _CacheConstants.FileExtensions.NUMPY_PARQUET_FILE_EXTENSION

            serializer_func = self._serialize_numpy_ndarray_as_parquet
        elif sparse.issparse(obj):
            ext = _CacheConstants.FileExtensions.SCIPY_SPARSE_FILE_EXTENSION
            serializer_func = self._serialize_scipy_sparse_matrix
        elif isinstance(obj, pd.DataFrame):
            ext = _CacheConstants.FileExtensions.DF_PARQUET_FILE_EXTENSION
            serializer_func = self._serialize_pandas_dataframe_as_parquet
        else:
            ext = _CacheConstants.FileExtensions.PICKLE_FILE_EXTENSION
            serializer_func = self._serialize_object_as_pickle

        deserialier_func = self._extension_to_deserializer.get(ext)
        full_name = ".".join([file_name, ext])
        serializer_func(full_name, obj)
        return CachedValue(path=os.path.join(self._root, full_name), func=deserialier_func)

    def _write(self, key: str, obj: Any) -> CachedValue:
        try:
            item = self._serialize(key, obj)
            self.cache_items[key] = item
            logger.info("Uploaded key: " + key)
            return item
        except Exception:
            logger.error("Uploading {} failed.".format(key))
            raise

    def _split_file_ext(self, path: str) -> Tuple[str, str]:
        """
        Given an arbitrary path with a file name and extension split path+file from extension. We first
        check with the FileExtensions that we use from `CacheConstants.FileExtensions`. If none of those match,
        we will continue with rfind towards the end. Keys might contain '.' so we can use rfind to get the separator
        then split file from extension.

        :param path: File path.
        :return: A tuple containing file name and extension.
        """
        for ext in _CacheConstants.FileExtensions.ALL:
            if path.endswith(ext):
                file_name = path[:len(path) - len(ext) - 1]
                return file_name, ext

        split = path.rfind(".")
        file_name = path[:split]
        ext = path[split + 1:]
        return file_name, ext
