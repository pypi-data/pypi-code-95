from ._cfs_provider import CFSProvider


def get_params(params: dict):
    params.pop("self")
    return params


class BaseDefinition:
    def __init__(self, **kwargs):
        self._kw = kwargs

        self._object_type = None

    async def get_data_async(self, session=None):
        file_store = CFSProvider(session=session)
        result = await file_store.get_data_async(
            object_type=self._object_type, **self._kw
        )
        return result

    def get_data(self, session=None):
        file_store = CFSProvider(session=session)
        return file_store.get_data(object_type=self._object_type, **self._kw)
