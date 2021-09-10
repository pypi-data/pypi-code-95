"""
Type annotations for kinesis-video-archived-media service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kinesis_video_archived_media/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_kinesis_video_archived_media import KinesisVideoArchivedMediaClient
    from mypy_boto3_kinesis_video_archived_media.paginator import (
        ListFragmentsPaginator,
    )

    client: KinesisVideoArchivedMediaClient = boto3.client("kinesis-video-archived-media")

    list_fragments_paginator: ListFragmentsPaginator = client.get_paginator("list_fragments")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import FragmentSelectorTypeDef, ListFragmentsOutputTypeDef, PaginatorConfigTypeDef

__all__ = ("ListFragmentsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListFragmentsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/kinesis-video-archived-media.html#KinesisVideoArchivedMedia.Paginator.ListFragments)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kinesis_video_archived_media/paginators.html#listfragmentspaginator)
    """

    def paginate(
        self,
        *,
        StreamName: str = None,
        StreamARN: str = None,
        FragmentSelector: "FragmentSelectorTypeDef" = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListFragmentsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/kinesis-video-archived-media.html#KinesisVideoArchivedMedia.Paginator.ListFragments.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kinesis_video_archived_media/paginators.html#listfragmentspaginator)
        """
