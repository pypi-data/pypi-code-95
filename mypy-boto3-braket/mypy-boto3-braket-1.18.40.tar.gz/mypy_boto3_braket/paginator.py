"""
Type annotations for braket service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_braket/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_braket import BraketClient
    from mypy_boto3_braket.paginator import (
        SearchDevicesPaginator,
        SearchQuantumTasksPaginator,
    )

    client: BraketClient = boto3.client("braket")

    search_devices_paginator: SearchDevicesPaginator = client.get_paginator("search_devices")
    search_quantum_tasks_paginator: SearchQuantumTasksPaginator = client.get_paginator("search_quantum_tasks")
    ```
"""
from typing import Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    PaginatorConfigTypeDef,
    SearchDevicesFilterTypeDef,
    SearchDevicesResponseTypeDef,
    SearchQuantumTasksFilterTypeDef,
    SearchQuantumTasksResponseTypeDef,
)

__all__ = ("SearchDevicesPaginator", "SearchQuantumTasksPaginator")


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class SearchDevicesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/braket.html#Braket.Paginator.SearchDevices)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_braket/paginators.html#searchdevicespaginator)
    """

    def paginate(
        self,
        *,
        filters: List["SearchDevicesFilterTypeDef"],
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[SearchDevicesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/braket.html#Braket.Paginator.SearchDevices.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_braket/paginators.html#searchdevicespaginator)
        """


class SearchQuantumTasksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/braket.html#Braket.Paginator.SearchQuantumTasks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_braket/paginators.html#searchquantumtaskspaginator)
    """

    def paginate(
        self,
        *,
        filters: List["SearchQuantumTasksFilterTypeDef"],
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[SearchQuantumTasksResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/braket.html#Braket.Paginator.SearchQuantumTasks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_braket/paginators.html#searchquantumtaskspaginator)
        """
