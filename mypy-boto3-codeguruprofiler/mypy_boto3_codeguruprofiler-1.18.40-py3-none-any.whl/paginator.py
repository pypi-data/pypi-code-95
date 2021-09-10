"""
Type annotations for codeguruprofiler service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguruprofiler/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_codeguruprofiler import CodeGuruProfilerClient
    from mypy_boto3_codeguruprofiler.paginator import (
        ListProfileTimesPaginator,
    )

    client: CodeGuruProfilerClient = boto3.client("codeguruprofiler")

    list_profile_times_paginator: ListProfileTimesPaginator = client.get_paginator("list_profile_times")
    ```
"""
from datetime import datetime
from typing import Generic, Iterator, TypeVar, Union

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import AggregationPeriodType, OrderByType
from .type_defs import ListProfileTimesResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListProfileTimesPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListProfileTimesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/codeguruprofiler.html#CodeGuruProfiler.Paginator.ListProfileTimes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguruprofiler/paginators.html#listprofiletimespaginator)
    """

    def paginate(
        self,
        *,
        endTime: Union[datetime, str],
        period: AggregationPeriodType,
        profilingGroupName: str,
        startTime: Union[datetime, str],
        orderBy: OrderByType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListProfileTimesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/codeguruprofiler.html#CodeGuruProfiler.Paginator.ListProfileTimes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguruprofiler/paginators.html#listprofiletimespaginator)
        """
