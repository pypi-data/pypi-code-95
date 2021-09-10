"""
Type annotations for mediastore-data service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediastore_data/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_mediastore_data import MediaStoreDataClient
    from mypy_boto3_mediastore_data.paginator import (
        ListItemsPaginator,
    )

    client: MediaStoreDataClient = boto3.client("mediastore-data")

    list_items_paginator: ListItemsPaginator = client.get_paginator("list_items")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import ListItemsResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListItemsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListItemsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/mediastore-data.html#MediaStoreData.Paginator.ListItems)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediastore_data/paginators.html#listitemspaginator)
    """

    def paginate(
        self, *, Path: str = None, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListItemsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/mediastore-data.html#MediaStoreData.Paginator.ListItems.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediastore_data/paginators.html#listitemspaginator)
        """
