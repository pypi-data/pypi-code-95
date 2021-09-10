"""
Type annotations for batch service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_batch import BatchClient
    from mypy_boto3_batch.paginator import (
        DescribeComputeEnvironmentsPaginator,
        DescribeJobDefinitionsPaginator,
        DescribeJobQueuesPaginator,
        ListJobsPaginator,
    )

    client: BatchClient = boto3.client("batch")

    describe_compute_environments_paginator: DescribeComputeEnvironmentsPaginator = client.get_paginator("describe_compute_environments")
    describe_job_definitions_paginator: DescribeJobDefinitionsPaginator = client.get_paginator("describe_job_definitions")
    describe_job_queues_paginator: DescribeJobQueuesPaginator = client.get_paginator("describe_job_queues")
    list_jobs_paginator: ListJobsPaginator = client.get_paginator("list_jobs")
    ```
"""
from typing import Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import JobStatusType
from .type_defs import (
    DescribeComputeEnvironmentsResponseTypeDef,
    DescribeJobDefinitionsResponseTypeDef,
    DescribeJobQueuesResponseTypeDef,
    KeyValuesPairTypeDef,
    ListJobsResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "DescribeComputeEnvironmentsPaginator",
    "DescribeJobDefinitionsPaginator",
    "DescribeJobQueuesPaginator",
    "ListJobsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeComputeEnvironmentsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.DescribeComputeEnvironments)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#describecomputeenvironmentspaginator)
    """

    def paginate(
        self,
        *,
        computeEnvironments: List[str] = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeComputeEnvironmentsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.DescribeComputeEnvironments.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#describecomputeenvironmentspaginator)
        """


class DescribeJobDefinitionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.DescribeJobDefinitions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#describejobdefinitionspaginator)
    """

    def paginate(
        self,
        *,
        jobDefinitions: List[str] = None,
        jobDefinitionName: str = None,
        status: str = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeJobDefinitionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.DescribeJobDefinitions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#describejobdefinitionspaginator)
        """


class DescribeJobQueuesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.DescribeJobQueues)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#describejobqueuespaginator)
    """

    def paginate(
        self, *, jobQueues: List[str] = None, PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeJobQueuesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.DescribeJobQueues.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#describejobqueuespaginator)
        """


class ListJobsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.ListJobs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#listjobspaginator)
    """

    def paginate(
        self,
        *,
        jobQueue: str = None,
        arrayJobId: str = None,
        multiNodeJobId: str = None,
        jobStatus: JobStatusType = None,
        filters: List["KeyValuesPairTypeDef"] = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[ListJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/batch.html#Batch.Paginator.ListJobs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_batch/paginators.html#listjobspaginator)
        """
