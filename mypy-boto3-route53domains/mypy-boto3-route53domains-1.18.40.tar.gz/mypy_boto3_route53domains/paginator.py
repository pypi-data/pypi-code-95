"""
Type annotations for route53domains service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_route53domains import Route53DomainsClient
    from mypy_boto3_route53domains.paginator import (
        ListDomainsPaginator,
        ListOperationsPaginator,
        ViewBillingPaginator,
    )

    client: Route53DomainsClient = boto3.client("route53domains")

    list_domains_paginator: ListDomainsPaginator = client.get_paginator("list_domains")
    list_operations_paginator: ListOperationsPaginator = client.get_paginator("list_operations")
    view_billing_paginator: ViewBillingPaginator = client.get_paginator("view_billing")
    ```
"""
from datetime import datetime
from typing import Generic, Iterator, TypeVar, Union

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    ListDomainsResponseTypeDef,
    ListOperationsResponseTypeDef,
    PaginatorConfigTypeDef,
    ViewBillingResponseTypeDef,
)

__all__ = ("ListDomainsPaginator", "ListOperationsPaginator", "ViewBillingPaginator")


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListDomainsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/route53domains.html#Route53Domains.Paginator.ListDomains)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html#listdomainspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListDomainsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/route53domains.html#Route53Domains.Paginator.ListDomains.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html#listdomainspaginator)
        """


class ListOperationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/route53domains.html#Route53Domains.Paginator.ListOperations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html#listoperationspaginator)
    """

    def paginate(
        self,
        *,
        SubmittedSince: Union[datetime, str] = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListOperationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/route53domains.html#Route53Domains.Paginator.ListOperations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html#listoperationspaginator)
        """


class ViewBillingPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/route53domains.html#Route53Domains.Paginator.ViewBilling)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html#viewbillingpaginator)
    """

    def paginate(
        self,
        *,
        Start: Union[datetime, str] = None,
        End: Union[datetime, str] = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ViewBillingResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/route53domains.html#Route53Domains.Paginator.ViewBilling.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53domains/paginators.html#viewbillingpaginator)
        """
