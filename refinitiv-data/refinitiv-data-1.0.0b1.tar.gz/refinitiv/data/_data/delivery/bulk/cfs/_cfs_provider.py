from pandas import DataFrame
from refinitiv.data._data.tools._common import urljoin

from ._cfs_type import CFSObjectType
from ._data_class import AttributesCFS
from ._tools import (
    _get_query_params,
    _get_query_parameter,
)
from ...data import Endpoint
from ....core.session import get_valid_session
from ....tools._utils import camel_to_snake


def _get_url(config, endpoint):
    base_url = config.get_str("url")
    endpoint_url = config.get_str(f"endpoints.{endpoint}")
    _url = urljoin(base_url, endpoint_url)
    return _url


class BaseCFSObject(AttributesCFS):
    def __init__(self, data, provider):
        self._data = {}
        super().__init__(provider, self._data)
        self._data.update({camel_to_snake(key): value for key, value in data.items()})
        self._child_objects = None
        self._provider = provider
        for name, value in self._data.items():
            setattr(self, name, value)

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        if self._child_type is None:
            raise TypeError(f"object {self._provider.name, type(self)} is not iterable")

        file_store = CFSProvider()
        args = self._params
        kwargs = {args[0]: self._data[args[1]]}

        self._child_objects = file_store.get_data(
            object_type=self._child_type, **kwargs
        )
        self._n = 0
        return self

    def __next__(self):
        _iter_obj = self._child_objects.data._iter_object
        if not _iter_obj:
            raise StopIteration
        if self._n < len(_iter_obj):
            result = self._child_objects.data._iter_object[self._n]
            self._n += 1
            return result
        raise StopIteration

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    @property
    def _params(self):
        raise NotImplementedError

    @property
    def _child_type(self):
        raise NotImplementedError


class CFSFile(BaseCFSObject):
    _child_type = None
    _params = None


class CFSBucket(BaseCFSObject):
    _child_type = CFSObjectType.FILESET
    _params = ("bucket", "name")


class CFSFileSet(BaseCFSObject):
    _child_type = CFSObjectType.FILE
    _params = ("fileset_id", "id")


class CFSPackage(BaseCFSObject):
    _child_type = CFSObjectType.FILESET
    _params = ("package_id", "package_id")

    def __init__(self, data, provider):
        super().__init__(data, provider)
        self._bucket_names = self._data["bucket_names"]

    def __iter__(self):
        file_store = CFSProvider()
        args = self._params
        kwargs = {args[0]: self._data[args[1]]}
        if not self._bucket_names:
            raise AttributeError("buckets not found")
        bucket_name = self._bucket_names[0]
        self._child_objects = file_store.get_data(
            object_type=CFSObjectType.FILESET,
            bucket=bucket_name,
            **kwargs,
        )
        self._n = 0
        return self

    def __next__(self):
        _iter_obj = self._child_objects.data._iter_object
        if not _iter_obj:
            raise StopIteration
        if self._n < len(_iter_obj):
            result = self._child_objects.data._iter_object[self._n]
            self._n += 1
            return result
        while self._bucket_names:
            bucket = self._bucket_names.pop(0)
            file_store = CFSProvider()
            args = self._params
            kwargs = {args[0]: self._data[args[1]]}
            self._child_objects = file_store.get_data(
                object_type=CFSObjectType.FILESET,
                bucket=bucket,
                **kwargs,
            )
            if (
                self._child_objects.error_code is None
                and self._child_objects.data.raw["value"]
            ):
                self._n = 0
                result = self._child_objects.data._iter_object[self._n]
                self._n += 1
                return result
        raise StopIteration


class_by_type = {
    CFSObjectType.BUCKET: CFSBucket,
    CFSObjectType.PACKAGE: CFSPackage,
    CFSObjectType.FILESET: CFSFileSet,
    CFSObjectType.FILE: CFSFile,
}

config_url_by_type = {
    CFSObjectType.BUCKET: "buckets",
    CFSObjectType.FILESET: "file-sets",
    CFSObjectType.PACKAGE: "packages",
    CFSObjectType.FILE: "files",
}


class IterObj:
    def __init__(self, value, provider=None):
        _class = class_by_type.get(provider)

        self._values = [_class(i, provider=provider) for i in value]

    def __getitem__(self, item):
        return self._values[item]

    def __iter__(self):
        self._n = 0
        return self

    def __next__(self):
        if self._n < len(self._values):
            result = self._values[self._n]
            self._n += 1
            return result
        raise StopIteration

    def __repr__(self):
        return "\n".join([repr(i) for i in self._values])

    def __len__(self):
        return len(self._values)


class CFSProvider:
    class Data(Endpoint.EndpointData):
        def __init__(self, raw_json, dataframe, iter_object=None):
            super().__init__(raw_json)
            self.raw["skip_token"] = _get_query_parameter(
                self.raw.get("@nextLink", None), "skipToken"
            )
            self._dataframe = dataframe
            self._iter_object = iter_object

    class BucketData(Data):
        @property
        def buckets(self):
            return self._iter_object

    class FileSetData(Data):
        @property
        def file_sets(self):
            return self._iter_object

    class PackageData(Data):
        @property
        def packages(self):
            return self._iter_object

    class FileData(Data):
        @property
        def files(self):
            return self._iter_object

    class Response(Endpoint.EndpointResponse):
        def __init__(self, result, object_type=None):
            data_type_by_type = {
                CFSObjectType.BUCKET: CFSProvider.BucketData,
                CFSObjectType.FILESET: CFSProvider.FileSetData,
                CFSObjectType.PACKAGE: CFSProvider.PackageData,
                CFSObjectType.FILE: CFSProvider.FileData,
            }
            _data_class = data_type_by_type.get(object_type, CFSProvider.Data)
            super().__init__(result._response)
            if self.is_success:
                self._value = self._data.raw["value"]
                _columns = set()
                for i in self._value:
                    _columns = _columns | i.keys()
                _columns = tuple(_columns)
                _data = [
                    [value[key] if key in value else None for key in _columns]
                    for value in self._value
                ]
                _dataframe = DataFrame(_data, columns=_columns)

                _iter_obj = IterObj(self._value, provider=object_type)
                self._data = _data_class(result.data.raw, _dataframe, _iter_obj)
            else:
                self._data = _data_class(self._data.raw, None, None)

    def __init__(self, session=None):
        session = get_valid_session(session)

        config = session._get_endpoint_config("file-store")
        _url = config.get_str("url")
        self._config = config

        self._data = None
        self._endpoint = Endpoint(session, _url)

    async def get_data_async(self, object_type, **kwargs):
        _query_parameters = _get_query_params(**kwargs)

        self._endpoint.url = _get_url(self._config, config_url_by_type.get(object_type))
        result = await self._endpoint.send_request_async(
            Endpoint.RequestMethod.GET, query_parameters=_query_parameters
        )
        return CFSProvider.Response(result, object_type=object_type)

    def get_data(self, object_type, **kwargs):
        result = self._endpoint.session._loop.run_until_complete(
            self.get_data_async(object_type, **kwargs)
        )
        return result

    async def get_stream_async(self, file_id):
        self._endpoint.url = urljoin(_get_url(self._config, "files"), "/{id}/stream")
        result = await self._endpoint.send_request_async(
            Endpoint.RequestMethod.GET,
            path_parameters={"id": file_id},
            query_parameters=(("doNotRedirect", "true"),),
        )
        return result

    def get_stream(self, file_id):
        result = self._endpoint.session._loop.run_until_complete(
            self.get_stream_async(file_id)
        )
        return result
