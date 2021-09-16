"""
Type annotations for kafkaconnect service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_kafkaconnect import KafkaConnectClient
    from mypy_boto3_kafkaconnect.paginator import (
        ListConnectorsPaginator,
        ListCustomPluginsPaginator,
        ListWorkerConfigurationsPaginator,
    )

    client: KafkaConnectClient = boto3.client("kafkaconnect")

    list_connectors_paginator: ListConnectorsPaginator = client.get_paginator("list_connectors")
    list_custom_plugins_paginator: ListCustomPluginsPaginator = client.get_paginator("list_custom_plugins")
    list_worker_configurations_paginator: ListWorkerConfigurationsPaginator = client.get_paginator("list_worker_configurations")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    ListConnectorsResponseTypeDef,
    ListCustomPluginsResponseTypeDef,
    ListWorkerConfigurationsResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "ListConnectorsPaginator",
    "ListCustomPluginsPaginator",
    "ListWorkerConfigurationsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListConnectorsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/kafkaconnect.html#KafkaConnect.Paginator.ListConnectors)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html#listconnectorspaginator)
    """

    def paginate(
        self, *, connectorNamePrefix: str = None, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListConnectorsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/kafkaconnect.html#KafkaConnect.Paginator.ListConnectors.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html#listconnectorspaginator)
        """


class ListCustomPluginsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/kafkaconnect.html#KafkaConnect.Paginator.ListCustomPlugins)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html#listcustompluginspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListCustomPluginsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/kafkaconnect.html#KafkaConnect.Paginator.ListCustomPlugins.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html#listcustompluginspaginator)
        """


class ListWorkerConfigurationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/kafkaconnect.html#KafkaConnect.Paginator.ListWorkerConfigurations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html#listworkerconfigurationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListWorkerConfigurationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/kafkaconnect.html#KafkaConnect.Paginator.ListWorkerConfigurations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafkaconnect/paginators.html#listworkerconfigurationspaginator)
        """
