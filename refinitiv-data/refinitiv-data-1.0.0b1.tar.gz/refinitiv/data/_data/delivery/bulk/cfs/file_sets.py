from typing import Optional

from ._cfs_type import CFSObjectType
from ._base_definition import BaseDefinition, get_params
from ._data_class import CFSFileSet
from ._tools import _convert_date_time


__all__ = ["Definition"]


class FileSetData:
    def __init__(self):
        self.file_sets = [CFSFileSet()]

    @property
    def raw(self):
        pass

    @property
    def df(self):
        pass


class Response:
    def __init__(self):
        self.data = FileSetData()


class Definition(BaseDefinition):
    def __init__(
        self,
        bucket: str,
        name: Optional[str] = None,
        attributes: Optional[dict] = None,
        package_id: Optional[str] = None,
        status: Optional[str] = None,
        available_from: Optional[str] = None,
        available_to: Optional[str] = None,
        content_from: Optional[str] = None,
        content_to: Optional[str] = None,
        created_since: Optional[str] = None,
        modified_since: Optional[str] = None,
        skip_token: Optional[str] = None,
        page_size: Optional[int] = 25,
    ):
        """
        Constructs all the necessary attributes for the Definition object.

        Parameters
        __________
            bucket : str
                The name of the bucket for file-sets to be searched.
                Only exactly matched results are returned.
            name : str, optional
                The name of the file-set. Only exactly matched results are returned.
            attributes : dict, optional
                Dict of publisher-defined key-value attributes.
            package_id : str, optional
            status : str, optional
                 Filter file-set by status (Ready/Pending).
            available_from : str, optional
                Filter results by when the file was made available.
                The date/time format is YYYY-MM-DDTHH:mm:ssZ.(e.g. 2020-01-21T04:19:01Z)
            available_to : str, optional
                Filter results by when the file was made available.
                The date/time format is YYYY-MM-DDTHH:mm:ssZ.(e.g. 2020-01-21T04:19:01Z)
            content_from : str, optional
                Filter results by the age of the content within the file.
                The date/time format is YYYY-MM-DDTHH:mm:ssZ.(e.g. 2020-01-21T04:19:01Z)
            content_to : str, optional
                Filter results by the age of the content within the file.
                The date/time format is YYYY-MM-DDTHH:mm:ssZ.(e.g. 2020-01-21T04:19:01Z)
            created_since : str, optional
                Filter results by the date/time the file was created.
                The date/time format is YYYY-MM-DDTHH:mm:ssZ.(e.g. 2020-01-21T04:19:01Z)
            modified_since : str, optional
                Filter results by the date/time the file was updated.
                The date/time format is YYYY-MM-DDTHH:mm:ssZ. (e.g. 2020-01-21T04:19:01Z)
            skip_token : str, optional
                Skip token is only used if a previous operation returned a partial result.
                If a previous response contains a nextLink element, the value of the nextLink
                element will include a skip token parameter that specifies a starting point to
                use for subsequent calls.
            page_size : int, optional
                Number of fileset returned.
                By default 25.

        Methods
        -------
        get_data(session=session)
            Returns a response to the data platform
        get_data_async(session=None)
            Returns a response asynchronously to the data platform

        Examples
        --------
         >>> from refinitiv.data.delivery.bulk import cfs
         >>> definition = cfs.file_sets.Definition()
         >>> file_sets = definition.get_data()

         Using get_data_async
         >>> import asyncio
         >>> task = asyncio.gather(
         ...    definition.get_data_async(),
         ...)
         >>> asyncio.get_event_loop().run_until_complete(task)
         >>> response, *_ = task._result
        """
        created_since = _convert_date_time(created_since)
        modified_since = _convert_date_time(modified_since)
        available_from = _convert_date_time(available_from)
        available_to = _convert_date_time(available_to)
        content_from = _convert_date_time(content_from)
        content_to = _convert_date_time(content_to)
        if attributes is not None:
            attributes = ",".join(
                [f"{key}:{value}" for key, value in attributes.items()]
            )
        super().__init__(**get_params(locals()))

        self._object_type = CFSObjectType.FILESET

    async def get_data_async(self, session=None) -> Response:
        response = super().get_data_async(session)
        return await response

    def get_data(self, session=None) -> Response:
        response = super().get_data(session)
        return response
