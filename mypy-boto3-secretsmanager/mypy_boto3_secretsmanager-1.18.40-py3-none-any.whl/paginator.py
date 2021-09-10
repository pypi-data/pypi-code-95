"""
Type annotations for secretsmanager service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_secretsmanager import SecretsManagerClient
    from mypy_boto3_secretsmanager.paginator import (
        ListSecretsPaginator,
    )

    client: SecretsManagerClient = boto3.client("secretsmanager")

    list_secrets_paginator: ListSecretsPaginator = client.get_paginator("list_secrets")
    ```
"""
from typing import Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import SortOrderTypeType
from .type_defs import FilterTypeDef, ListSecretsResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListSecretsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListSecretsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/secretsmanager.html#SecretsManager.Paginator.ListSecrets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/paginators.html#listsecretspaginator)
    """

    def paginate(
        self,
        *,
        Filters: List["FilterTypeDef"] = None,
        SortOrder: SortOrderTypeType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListSecretsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/secretsmanager.html#SecretsManager.Paginator.ListSecrets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/paginators.html#listsecretspaginator)
        """
