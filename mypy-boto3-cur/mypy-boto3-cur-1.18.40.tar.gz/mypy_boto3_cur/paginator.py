"""
Type annotations for cur service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cur/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_cur import CostandUsageReportServiceClient
    from mypy_boto3_cur.paginator import (
        DescribeReportDefinitionsPaginator,
    )

    client: CostandUsageReportServiceClient = boto3.client("cur")

    describe_report_definitions_paginator: DescribeReportDefinitionsPaginator = client.get_paginator("describe_report_definitions")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import DescribeReportDefinitionsResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("DescribeReportDefinitionsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeReportDefinitionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/cur.html#CostandUsageReportService.Paginator.DescribeReportDefinitions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cur/paginators.html#describereportdefinitionspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeReportDefinitionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/cur.html#CostandUsageReportService.Paginator.DescribeReportDefinitions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cur/paginators.html#describereportdefinitionspaginator)
        """
