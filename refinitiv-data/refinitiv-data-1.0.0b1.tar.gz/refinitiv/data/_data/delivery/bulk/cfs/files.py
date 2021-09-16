from datetime import timedelta, datetime
from typing import Union, Optional

from ._cfs_type import CFSObjectType
from ._base_definition import BaseDefinition, get_params
from ._data_class import CFSFile
from ._tools import _convert_date_time

__all__ = ["Definition"]


class FileData:
    def __init__(self):
        self.files = [CFSFile()]

    @property
    def raw(self):
        pass

    @property
    def df(self):
        pass


class Response:
    def __init__(self):
        self.data = FileData()


class Definition(BaseDefinition):
    def __init__(
        self,
        fileset_id: str,
        file_name: Optional[str] = None,
        created_since: Union[str, datetime, timedelta] = None,
        modified_since: Union[str, datetime, timedelta] = None,
        skip_token: Optional[str] = None,
        page_size: Optional[int] = 25,
    ):
        """
        Constructs all the necessary attributes for the Definition object.

        Parameters
        __________
            fileset_id : str
                The name of the file-set for files to be searched.
                Only exactly matched results are returned.
            file_name : str, optional
                Filter results by file name.
            created_since : str or timedelta or datetime, optional
                Filter results by when the Bucket was created.
            modified_since : str or timedelta or datetime, optional
                Filter results by when the Bucket was last modified.
            skip_token : str, optional
                Used for server-side paging.
            page_size : int, optional
                Used for server-side paging.
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
         >>> definition = cfs.files.Definition()
         >>> files = definition.get_data()

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
        super().__init__(**get_params(locals()))

        self._object_type = CFSObjectType.FILE

    async def get_data_async(self, session=None) -> Response:
        response = super().get_data_async(session)
        return await response

    def get_data(self, session=None) -> Response:
        response = super().get_data(session)
        return response
