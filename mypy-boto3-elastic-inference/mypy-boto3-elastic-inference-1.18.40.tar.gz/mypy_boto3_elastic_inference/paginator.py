"""
Type annotations for elastic-inference service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elastic_inference/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_elastic_inference import ElasticInferenceClient
    from mypy_boto3_elastic_inference.paginator import (
        DescribeAcceleratorsPaginator,
    )

    client: ElasticInferenceClient = boto3.client("elastic-inference")

    describe_accelerators_paginator: DescribeAcceleratorsPaginator = client.get_paginator("describe_accelerators")
    ```
"""
from typing import Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import DescribeAcceleratorsResponseTypeDef, FilterTypeDef, PaginatorConfigTypeDef

__all__ = ("DescribeAcceleratorsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeAcceleratorsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/elastic-inference.html#ElasticInference.Paginator.DescribeAccelerators)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elastic_inference/paginators.html#describeacceleratorspaginator)
    """

    def paginate(
        self,
        *,
        acceleratorIds: List[str] = None,
        filters: List["FilterTypeDef"] = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeAcceleratorsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/elastic-inference.html#ElasticInference.Paginator.DescribeAccelerators.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elastic_inference/paginators.html#describeacceleratorspaginator)
        """
