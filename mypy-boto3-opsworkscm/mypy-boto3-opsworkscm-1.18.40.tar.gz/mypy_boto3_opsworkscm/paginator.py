"""
Type annotations for opsworkscm service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_opsworkscm import OpsWorksCMClient
    from mypy_boto3_opsworkscm.paginator import (
        DescribeBackupsPaginator,
        DescribeEventsPaginator,
        DescribeServersPaginator,
        ListTagsForResourcePaginator,
    )

    client: OpsWorksCMClient = boto3.client("opsworkscm")

    describe_backups_paginator: DescribeBackupsPaginator = client.get_paginator("describe_backups")
    describe_events_paginator: DescribeEventsPaginator = client.get_paginator("describe_events")
    describe_servers_paginator: DescribeServersPaginator = client.get_paginator("describe_servers")
    list_tags_for_resource_paginator: ListTagsForResourcePaginator = client.get_paginator("list_tags_for_resource")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    DescribeBackupsResponseTypeDef,
    DescribeEventsResponseTypeDef,
    DescribeServersResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "DescribeBackupsPaginator",
    "DescribeEventsPaginator",
    "DescribeServersPaginator",
    "ListTagsForResourcePaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeBackupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.DescribeBackups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#describebackupspaginator)
    """

    def paginate(
        self,
        *,
        BackupId: str = None,
        ServerName: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeBackupsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.DescribeBackups.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#describebackupspaginator)
        """


class DescribeEventsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.DescribeEvents)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#describeeventspaginator)
    """

    def paginate(
        self, *, ServerName: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeEventsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.DescribeEvents.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#describeeventspaginator)
        """


class DescribeServersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.DescribeServers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#describeserverspaginator)
    """

    def paginate(
        self, *, ServerName: str = None, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeServersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.DescribeServers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#describeserverspaginator)
        """


class ListTagsForResourcePaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.ListTagsForResource)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#listtagsforresourcepaginator)
    """

    def paginate(
        self, *, ResourceArn: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListTagsForResourceResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/opsworkscm.html#OpsWorksCM.Paginator.ListTagsForResource.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworkscm/paginators.html#listtagsforresourcepaginator)
        """
