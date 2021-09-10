"""
Type annotations for glue service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_glue import GlueClient
    from mypy_boto3_glue.paginator import (
        GetClassifiersPaginator,
        GetConnectionsPaginator,
        GetCrawlerMetricsPaginator,
        GetCrawlersPaginator,
        GetDatabasesPaginator,
        GetDevEndpointsPaginator,
        GetJobRunsPaginator,
        GetJobsPaginator,
        GetPartitionIndexesPaginator,
        GetPartitionsPaginator,
        GetResourcePoliciesPaginator,
        GetSecurityConfigurationsPaginator,
        GetTableVersionsPaginator,
        GetTablesPaginator,
        GetTriggersPaginator,
        GetUserDefinedFunctionsPaginator,
        ListRegistriesPaginator,
        ListSchemaVersionsPaginator,
        ListSchemasPaginator,
    )

    client: GlueClient = boto3.client("glue")

    get_classifiers_paginator: GetClassifiersPaginator = client.get_paginator("get_classifiers")
    get_connections_paginator: GetConnectionsPaginator = client.get_paginator("get_connections")
    get_crawler_metrics_paginator: GetCrawlerMetricsPaginator = client.get_paginator("get_crawler_metrics")
    get_crawlers_paginator: GetCrawlersPaginator = client.get_paginator("get_crawlers")
    get_databases_paginator: GetDatabasesPaginator = client.get_paginator("get_databases")
    get_dev_endpoints_paginator: GetDevEndpointsPaginator = client.get_paginator("get_dev_endpoints")
    get_job_runs_paginator: GetJobRunsPaginator = client.get_paginator("get_job_runs")
    get_jobs_paginator: GetJobsPaginator = client.get_paginator("get_jobs")
    get_partition_indexes_paginator: GetPartitionIndexesPaginator = client.get_paginator("get_partition_indexes")
    get_partitions_paginator: GetPartitionsPaginator = client.get_paginator("get_partitions")
    get_resource_policies_paginator: GetResourcePoliciesPaginator = client.get_paginator("get_resource_policies")
    get_security_configurations_paginator: GetSecurityConfigurationsPaginator = client.get_paginator("get_security_configurations")
    get_table_versions_paginator: GetTableVersionsPaginator = client.get_paginator("get_table_versions")
    get_tables_paginator: GetTablesPaginator = client.get_paginator("get_tables")
    get_triggers_paginator: GetTriggersPaginator = client.get_paginator("get_triggers")
    get_user_defined_functions_paginator: GetUserDefinedFunctionsPaginator = client.get_paginator("get_user_defined_functions")
    list_registries_paginator: ListRegistriesPaginator = client.get_paginator("list_registries")
    list_schema_versions_paginator: ListSchemaVersionsPaginator = client.get_paginator("list_schema_versions")
    list_schemas_paginator: ListSchemasPaginator = client.get_paginator("list_schemas")
    ```
"""
from typing import Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import ResourceShareTypeType
from .type_defs import (
    GetClassifiersResponseTypeDef,
    GetConnectionsFilterTypeDef,
    GetConnectionsResponseTypeDef,
    GetCrawlerMetricsResponseTypeDef,
    GetCrawlersResponseTypeDef,
    GetDatabasesResponseTypeDef,
    GetDevEndpointsResponseTypeDef,
    GetJobRunsResponseTypeDef,
    GetJobsResponseTypeDef,
    GetPartitionIndexesResponseTypeDef,
    GetPartitionsResponseTypeDef,
    GetResourcePoliciesResponseTypeDef,
    GetSecurityConfigurationsResponseTypeDef,
    GetTablesResponseTypeDef,
    GetTableVersionsResponseTypeDef,
    GetTriggersResponseTypeDef,
    GetUserDefinedFunctionsResponseTypeDef,
    ListRegistriesResponseTypeDef,
    ListSchemasResponseTypeDef,
    ListSchemaVersionsResponseTypeDef,
    PaginatorConfigTypeDef,
    RegistryIdTypeDef,
    SchemaIdTypeDef,
    SegmentTypeDef,
)

__all__ = (
    "GetClassifiersPaginator",
    "GetConnectionsPaginator",
    "GetCrawlerMetricsPaginator",
    "GetCrawlersPaginator",
    "GetDatabasesPaginator",
    "GetDevEndpointsPaginator",
    "GetJobRunsPaginator",
    "GetJobsPaginator",
    "GetPartitionIndexesPaginator",
    "GetPartitionsPaginator",
    "GetResourcePoliciesPaginator",
    "GetSecurityConfigurationsPaginator",
    "GetTableVersionsPaginator",
    "GetTablesPaginator",
    "GetTriggersPaginator",
    "GetUserDefinedFunctionsPaginator",
    "ListRegistriesPaginator",
    "ListSchemaVersionsPaginator",
    "ListSchemasPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class GetClassifiersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetClassifiers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getclassifierspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetClassifiersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetClassifiers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getclassifierspaginator)
        """


class GetConnectionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetConnections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getconnectionspaginator)
    """

    def paginate(
        self,
        *,
        CatalogId: str = None,
        Filter: "GetConnectionsFilterTypeDef" = None,
        HidePassword: bool = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetConnectionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetConnections.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getconnectionspaginator)
        """


class GetCrawlerMetricsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetCrawlerMetrics)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getcrawlermetricspaginator)
    """

    def paginate(
        self, *, CrawlerNameList: List[str] = None, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetCrawlerMetricsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetCrawlerMetrics.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getcrawlermetricspaginator)
        """


class GetCrawlersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetCrawlers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getcrawlerspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetCrawlersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetCrawlers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getcrawlerspaginator)
        """


class GetDatabasesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetDatabases)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getdatabasespaginator)
    """

    def paginate(
        self,
        *,
        CatalogId: str = None,
        ResourceShareType: ResourceShareTypeType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetDatabasesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetDatabases.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getdatabasespaginator)
        """


class GetDevEndpointsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetDevEndpoints)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getdevendpointspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetDevEndpointsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetDevEndpoints.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getdevendpointspaginator)
        """


class GetJobRunsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetJobRuns)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getjobrunspaginator)
    """

    def paginate(
        self, *, JobName: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetJobRunsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetJobRuns.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getjobrunspaginator)
        """


class GetJobsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetJobs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getjobspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetJobs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getjobspaginator)
        """


class GetPartitionIndexesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetPartitionIndexes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getpartitionindexespaginator)
    """

    def paginate(
        self,
        *,
        DatabaseName: str,
        TableName: str,
        CatalogId: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetPartitionIndexesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetPartitionIndexes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getpartitionindexespaginator)
        """


class GetPartitionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetPartitions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getpartitionspaginator)
    """

    def paginate(
        self,
        *,
        DatabaseName: str,
        TableName: str,
        CatalogId: str = None,
        Expression: str = None,
        Segment: "SegmentTypeDef" = None,
        ExcludeColumnSchema: bool = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetPartitionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetPartitions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getpartitionspaginator)
        """


class GetResourcePoliciesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetResourcePolicies)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getresourcepoliciespaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetResourcePoliciesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetResourcePolicies.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getresourcepoliciespaginator)
        """


class GetSecurityConfigurationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetSecurityConfigurations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getsecurityconfigurationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetSecurityConfigurationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetSecurityConfigurations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getsecurityconfigurationspaginator)
        """


class GetTableVersionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetTableVersions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#gettableversionspaginator)
    """

    def paginate(
        self,
        *,
        DatabaseName: str,
        TableName: str,
        CatalogId: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetTableVersionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetTableVersions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#gettableversionspaginator)
        """


class GetTablesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetTables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#gettablespaginator)
    """

    def paginate(
        self,
        *,
        DatabaseName: str,
        CatalogId: str = None,
        Expression: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetTablesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetTables.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#gettablespaginator)
        """


class GetTriggersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetTriggers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#gettriggerspaginator)
    """

    def paginate(
        self, *, DependentJobName: str = None, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetTriggersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetTriggers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#gettriggerspaginator)
        """


class GetUserDefinedFunctionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetUserDefinedFunctions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getuserdefinedfunctionspaginator)
    """

    def paginate(
        self,
        *,
        Pattern: str,
        CatalogId: str = None,
        DatabaseName: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetUserDefinedFunctionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.GetUserDefinedFunctions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#getuserdefinedfunctionspaginator)
        """


class ListRegistriesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.ListRegistries)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#listregistriespaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListRegistriesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.ListRegistries.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#listregistriespaginator)
        """


class ListSchemaVersionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.ListSchemaVersions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#listschemaversionspaginator)
    """

    def paginate(
        self, *, SchemaId: "SchemaIdTypeDef", PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListSchemaVersionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.ListSchemaVersions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#listschemaversionspaginator)
        """


class ListSchemasPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.ListSchemas)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#listschemaspaginator)
    """

    def paginate(
        self,
        *,
        RegistryId: "RegistryIdTypeDef" = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListSchemasResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/glue.html#Glue.Paginator.ListSchemas.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_glue/paginators.html#listschemaspaginator)
        """
