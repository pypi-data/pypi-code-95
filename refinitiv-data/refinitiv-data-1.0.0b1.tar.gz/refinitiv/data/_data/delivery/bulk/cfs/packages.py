from typing import Optional

from ._cfs_type import CFSObjectType
from ._data_class import CFSPackage
from ._base_definition import BaseDefinition, get_params


__all__ = ["Definition"]


class PackageData:
    def __init__(self):
        self.packages = [CFSPackage()]

    @property
    def raw(self):
        pass

    @property
    def df(self):
        pass


class Response:
    def __init__(self):
        self.data = PackageData()


class Definition(BaseDefinition):
    def __init__(
        self,
        package_name: Optional[str] = None,
        package_type: Optional[str] = None,
        bucket_name: Optional[str] = None,
        page: Optional[int] = None,
        included_total_result: Optional[bool] = False,
        skip_token: Optional[str] = None,
        page_size: Optional[int] = 25,
        included_entitlement_result: Optional[bool] = False,
    ):
        """
        Constructs all the necessary attributes for the Definition object.

        Parameters
        __________
            package_name : str, optional
                Filter results by package name. (Partial match).
            package_type : str, optional
                Filter results by package type.
                Available values : core, bulk, private.
            bucket_name : str, optional
                List the package that associated with this bucket.
            page : int, optional
                The offest number determine which set of result should be
                returned from all results.
            included_total_result : bool, optional
                The flag to indicate if total record count should be returned.
                By default False.
            skip_token : str, optional
                Skip token is only used if a previous operation returned a partial result.
                If a previous response contains a nextLink element, the value of the nextLink
                element will include a skip token parameter that specifies a starting point to use
                for subsequent calls.
            page_size : int, optional
                The number of package that will be returned into a single response.
                By default 25.
            included_entitlement_result : bool, optional
                The flag to indicate the entitlement checking on each package.
                By default False.

        Methods
        -------
        get_data(session=session)
            Returns a response to the data platform
        get_data_async(session=None)
            Returns a response asynchronously to the data platform

        Examples
        --------
         >>> from refinitiv.data.delivery.bulk import cfs
         >>> definition = cfs.packages.Definition()
         >>> packages = definition.get_data()

         Using get_data_async
         >>> import asyncio
         >>> task = asyncio.gather(
         ...    definition.get_data_async(),
         ...)
         >>> asyncio.get_event_loop().run_until_complete(task)
         >>> response, *_ = task._result
        """
        super().__init__(**get_params(locals()))

        self._object_type = CFSObjectType.PACKAGE

    async def get_data_async(self, session=None) -> Response:
        response = super().get_data_async(session)
        return await response

    def get_data(self, session=None) -> Response:
        response = super().get_data(session)
        return response
