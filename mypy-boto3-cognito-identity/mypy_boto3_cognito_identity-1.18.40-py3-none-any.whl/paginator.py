"""
Type annotations for cognito-identity service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cognito_identity/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_cognito_identity import CognitoIdentityClient
    from mypy_boto3_cognito_identity.paginator import (
        ListIdentityPoolsPaginator,
    )

    client: CognitoIdentityClient = boto3.client("cognito-identity")

    list_identity_pools_paginator: ListIdentityPoolsPaginator = client.get_paginator("list_identity_pools")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import ListIdentityPoolsResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListIdentityPoolsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListIdentityPoolsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/cognito-identity.html#CognitoIdentity.Paginator.ListIdentityPools)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cognito_identity/paginators.html#listidentitypoolspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListIdentityPoolsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/cognito-identity.html#CognitoIdentity.Paginator.ListIdentityPools.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cognito_identity/paginators.html#listidentitypoolspaginator)
        """
