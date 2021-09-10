"""
Type annotations for appsync service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_appsync import AppSyncClient
    from mypy_boto3_appsync.paginator import (
        ListApiKeysPaginator,
        ListDataSourcesPaginator,
        ListFunctionsPaginator,
        ListGraphqlApisPaginator,
        ListResolversPaginator,
        ListResolversByFunctionPaginator,
        ListTypesPaginator,
    )

    client: AppSyncClient = boto3.client("appsync")

    list_api_keys_paginator: ListApiKeysPaginator = client.get_paginator("list_api_keys")
    list_data_sources_paginator: ListDataSourcesPaginator = client.get_paginator("list_data_sources")
    list_functions_paginator: ListFunctionsPaginator = client.get_paginator("list_functions")
    list_graphql_apis_paginator: ListGraphqlApisPaginator = client.get_paginator("list_graphql_apis")
    list_resolvers_paginator: ListResolversPaginator = client.get_paginator("list_resolvers")
    list_resolvers_by_function_paginator: ListResolversByFunctionPaginator = client.get_paginator("list_resolvers_by_function")
    list_types_paginator: ListTypesPaginator = client.get_paginator("list_types")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import TypeDefinitionFormatType
from .type_defs import (
    ListApiKeysResponseTypeDef,
    ListDataSourcesResponseTypeDef,
    ListFunctionsResponseTypeDef,
    ListGraphqlApisResponseTypeDef,
    ListResolversByFunctionResponseTypeDef,
    ListResolversResponseTypeDef,
    ListTypesResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "ListApiKeysPaginator",
    "ListDataSourcesPaginator",
    "ListFunctionsPaginator",
    "ListGraphqlApisPaginator",
    "ListResolversPaginator",
    "ListResolversByFunctionPaginator",
    "ListTypesPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListApiKeysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListApiKeys)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listapikeyspaginator)
    """

    def paginate(
        self, *, apiId: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListApiKeysResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListApiKeys.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listapikeyspaginator)
        """


class ListDataSourcesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListDataSources)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listdatasourcespaginator)
    """

    def paginate(
        self, *, apiId: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListDataSourcesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListDataSources.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listdatasourcespaginator)
        """


class ListFunctionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListFunctions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listfunctionspaginator)
    """

    def paginate(
        self, *, apiId: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListFunctionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListFunctions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listfunctionspaginator)
        """


class ListGraphqlApisPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListGraphqlApis)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listgraphqlapispaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListGraphqlApisResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListGraphqlApis.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listgraphqlapispaginator)
        """


class ListResolversPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListResolvers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listresolverspaginator)
    """

    def paginate(
        self, *, apiId: str, typeName: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListResolversResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListResolvers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listresolverspaginator)
        """


class ListResolversByFunctionPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListResolversByFunction)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listresolversbyfunctionpaginator)
    """

    def paginate(
        self, *, apiId: str, functionId: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListResolversByFunctionResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListResolversByFunction.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listresolversbyfunctionpaginator)
        """


class ListTypesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListTypes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listtypespaginator)
    """

    def paginate(
        self,
        *,
        apiId: str,
        format: TypeDefinitionFormatType,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListTypesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/appsync.html#AppSync.Paginator.ListTypes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_appsync/paginators.html#listtypespaginator)
        """
