"""
Type annotations for marketplace-entitlement service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_marketplace_entitlement/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_marketplace_entitlement import MarketplaceEntitlementServiceClient
    from mypy_boto3_marketplace_entitlement.paginator import (
        GetEntitlementsPaginator,
    )

    client: MarketplaceEntitlementServiceClient = boto3.client("marketplace-entitlement")

    get_entitlements_paginator: GetEntitlementsPaginator = client.get_paginator("get_entitlements")
    ```
"""
from typing import Dict, Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import GetEntitlementFilterNameType
from .type_defs import GetEntitlementsResultTypeDef, PaginatorConfigTypeDef

__all__ = ("GetEntitlementsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class GetEntitlementsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/marketplace-entitlement.html#MarketplaceEntitlementService.Paginator.GetEntitlements)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_marketplace_entitlement/paginators.html#getentitlementspaginator)
    """

    def paginate(
        self,
        *,
        ProductCode: str,
        Filter: Dict[GetEntitlementFilterNameType, List[str]] = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetEntitlementsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/marketplace-entitlement.html#MarketplaceEntitlementService.Paginator.GetEntitlements.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_marketplace_entitlement/paginators.html#getentitlementspaginator)
        """
