"""
Type annotations for application-autoscaling service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_application_autoscaling import ApplicationAutoScalingClient
    from mypy_boto3_application_autoscaling.paginator import (
        DescribeScalableTargetsPaginator,
        DescribeScalingActivitiesPaginator,
        DescribeScalingPoliciesPaginator,
        DescribeScheduledActionsPaginator,
    )

    client: ApplicationAutoScalingClient = boto3.client("application-autoscaling")

    describe_scalable_targets_paginator: DescribeScalableTargetsPaginator = client.get_paginator("describe_scalable_targets")
    describe_scaling_activities_paginator: DescribeScalingActivitiesPaginator = client.get_paginator("describe_scaling_activities")
    describe_scaling_policies_paginator: DescribeScalingPoliciesPaginator = client.get_paginator("describe_scaling_policies")
    describe_scheduled_actions_paginator: DescribeScheduledActionsPaginator = client.get_paginator("describe_scheduled_actions")
    ```
"""
from typing import Generic, Iterator, List, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import ScalableDimensionType, ServiceNamespaceType
from .type_defs import (
    DescribeScalableTargetsResponseTypeDef,
    DescribeScalingActivitiesResponseTypeDef,
    DescribeScalingPoliciesResponseTypeDef,
    DescribeScheduledActionsResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "DescribeScalableTargetsPaginator",
    "DescribeScalingActivitiesPaginator",
    "DescribeScalingPoliciesPaginator",
    "DescribeScheduledActionsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeScalableTargetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScalableTargets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescalabletargetspaginator)
    """

    def paginate(
        self,
        *,
        ServiceNamespace: ServiceNamespaceType,
        ResourceIds: List[str] = None,
        ScalableDimension: ScalableDimensionType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeScalableTargetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScalableTargets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescalabletargetspaginator)
        """


class DescribeScalingActivitiesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScalingActivities)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescalingactivitiespaginator)
    """

    def paginate(
        self,
        *,
        ServiceNamespace: ServiceNamespaceType,
        ResourceId: str = None,
        ScalableDimension: ScalableDimensionType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeScalingActivitiesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScalingActivities.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescalingactivitiespaginator)
        """


class DescribeScalingPoliciesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScalingPolicies)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescalingpoliciespaginator)
    """

    def paginate(
        self,
        *,
        ServiceNamespace: ServiceNamespaceType,
        PolicyNames: List[str] = None,
        ResourceId: str = None,
        ScalableDimension: ScalableDimensionType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeScalingPoliciesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScalingPolicies.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescalingpoliciespaginator)
        """


class DescribeScheduledActionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScheduledActions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescheduledactionspaginator)
    """

    def paginate(
        self,
        *,
        ServiceNamespace: ServiceNamespaceType,
        ScheduledActionNames: List[str] = None,
        ResourceId: str = None,
        ScalableDimension: ScalableDimensionType = None,
        PaginationConfig: PaginatorConfigTypeDef = None
    ) -> _PageIterator[DescribeScheduledActionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.40/reference/services/application-autoscaling.html#ApplicationAutoScaling.Paginator.DescribeScheduledActions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_application_autoscaling/paginators.html#describescheduledactionspaginator)
        """
