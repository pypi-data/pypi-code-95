"""
Type annotations for redshift-data service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_redshift_data import RedshiftDataAPIServiceClient
    from mypy_boto3_redshift_data.paginator import (
        DescribeTablePaginator,
        GetStatementResultPaginator,
        ListDatabasesPaginator,
        ListSchemasPaginator,
        ListStatementsPaginator,
        ListTablesPaginator,
    )

    client: RedshiftDataAPIServiceClient = boto3.client("redshift-data")

    describe_table_paginator: DescribeTablePaginator = client.get_paginator("describe_table")
    get_statement_result_paginator: GetStatementResultPaginator = client.get_paginator("get_statement_result")
    list_databases_paginator: ListDatabasesPaginator = client.get_paginator("list_databases")
    list_schemas_paginator: ListSchemasPaginator = client.get_paginator("list_schemas")
    list_statements_paginator: ListStatementsPaginator = client.get_paginator("list_statements")
    list_tables_paginator: ListTablesPaginator = client.get_paginator("list_tables")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import StatusStringType
from .type_defs import (
    DescribeTableResponseTypeDef,
    GetStatementResultResponseTypeDef,
    ListDatabasesResponseTypeDef,
    ListSchemasResponseTypeDef,
    ListStatementsResponseTypeDef,
    ListTablesResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "DescribeTablePaginator",
    "GetStatementResultPaginator",
    "ListDatabasesPaginator",
    "ListSchemasPaginator",
    "ListStatementsPaginator",
    "ListTablesPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeTablePaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.DescribeTable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#describetablepaginator)
    """

    def paginate(
        self,
        *,
        ClusterIdentifier: str,
        Database: str,
        ConnectedDatabase: str = None,
        DbUser: str = None,
        Schema: str = None,
        SecretArn: str = None,
        Table: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeTableResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.DescribeTable.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#describetablepaginator)
        """


class GetStatementResultPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.GetStatementResult)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#getstatementresultpaginator)
    """

    def paginate(
        self, *, Id: str, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[GetStatementResultResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.GetStatementResult.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#getstatementresultpaginator)
        """


class ListDatabasesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListDatabases)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#listdatabasespaginator)
    """

    def paginate(
        self,
        *,
        ClusterIdentifier: str,
        Database: str,
        DbUser: str = None,
        SecretArn: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListDatabasesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListDatabases.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#listdatabasespaginator)
        """


class ListSchemasPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListSchemas)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#listschemaspaginator)
    """

    def paginate(
        self,
        *,
        ClusterIdentifier: str,
        Database: str,
        ConnectedDatabase: str = None,
        DbUser: str = None,
        SchemaPattern: str = None,
        SecretArn: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListSchemasResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListSchemas.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#listschemaspaginator)
        """


class ListStatementsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListStatements)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#liststatementspaginator)
    """

    def paginate(
        self,
        *,
        RoleLevel: bool = None,
        StatementName: str = None,
        Status: StatusStringType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListStatementsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListStatements.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#liststatementspaginator)
        """


class ListTablesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListTables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#listtablespaginator)
    """

    def paginate(
        self,
        *,
        ClusterIdentifier: str,
        Database: str,
        ConnectedDatabase: str = None,
        DbUser: str = None,
        SchemaPattern: str = None,
        SecretArn: str = None,
        TablePattern: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListTablesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/redshift-data.html#RedshiftDataAPIService.Paginator.ListTables.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift_data/paginators.html#listtablespaginator)
        """
