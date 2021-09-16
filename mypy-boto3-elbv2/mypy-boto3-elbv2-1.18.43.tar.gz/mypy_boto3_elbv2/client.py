"""
Type annotations for elbv2 service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_elbv2 import ElasticLoadBalancingv2Client

    client: ElasticLoadBalancingv2Client = boto3.client("elbv2")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    IpAddressTypeType,
    LoadBalancerSchemeEnumType,
    LoadBalancerTypeEnumType,
    ProtocolEnumType,
    TargetTypeEnumType,
)
from .paginator import (
    DescribeAccountLimitsPaginator,
    DescribeListenerCertificatesPaginator,
    DescribeListenersPaginator,
    DescribeLoadBalancersPaginator,
    DescribeRulesPaginator,
    DescribeSSLPoliciesPaginator,
    DescribeTargetGroupsPaginator,
)
from .type_defs import (
    ActionTypeDef,
    AddListenerCertificatesOutputTypeDef,
    CertificateTypeDef,
    CreateListenerOutputTypeDef,
    CreateLoadBalancerOutputTypeDef,
    CreateRuleOutputTypeDef,
    CreateTargetGroupOutputTypeDef,
    DescribeAccountLimitsOutputTypeDef,
    DescribeListenerCertificatesOutputTypeDef,
    DescribeListenersOutputTypeDef,
    DescribeLoadBalancerAttributesOutputTypeDef,
    DescribeLoadBalancersOutputTypeDef,
    DescribeRulesOutputTypeDef,
    DescribeSSLPoliciesOutputTypeDef,
    DescribeTagsOutputTypeDef,
    DescribeTargetGroupAttributesOutputTypeDef,
    DescribeTargetGroupsOutputTypeDef,
    DescribeTargetHealthOutputTypeDef,
    LoadBalancerAttributeTypeDef,
    MatcherTypeDef,
    ModifyListenerOutputTypeDef,
    ModifyLoadBalancerAttributesOutputTypeDef,
    ModifyRuleOutputTypeDef,
    ModifyTargetGroupAttributesOutputTypeDef,
    ModifyTargetGroupOutputTypeDef,
    RuleConditionTypeDef,
    RulePriorityPairTypeDef,
    SetIpAddressTypeOutputTypeDef,
    SetRulePrioritiesOutputTypeDef,
    SetSecurityGroupsOutputTypeDef,
    SetSubnetsOutputTypeDef,
    SubnetMappingTypeDef,
    TagTypeDef,
    TargetDescriptionTypeDef,
    TargetGroupAttributeTypeDef,
)
from .waiter import (
    LoadBalancerAvailableWaiter,
    LoadBalancerExistsWaiter,
    LoadBalancersDeletedWaiter,
    TargetDeregisteredWaiter,
    TargetInServiceWaiter,
)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("ElasticLoadBalancingv2Client",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    ALPNPolicyNotSupportedException: Type[BotocoreClientError]
    AllocationIdNotFoundException: Type[BotocoreClientError]
    AvailabilityZoneNotSupportedException: Type[BotocoreClientError]
    CertificateNotFoundException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    DuplicateListenerException: Type[BotocoreClientError]
    DuplicateLoadBalancerNameException: Type[BotocoreClientError]
    DuplicateTagKeysException: Type[BotocoreClientError]
    DuplicateTargetGroupNameException: Type[BotocoreClientError]
    HealthUnavailableException: Type[BotocoreClientError]
    IncompatibleProtocolsException: Type[BotocoreClientError]
    InvalidConfigurationRequestException: Type[BotocoreClientError]
    InvalidLoadBalancerActionException: Type[BotocoreClientError]
    InvalidSchemeException: Type[BotocoreClientError]
    InvalidSecurityGroupException: Type[BotocoreClientError]
    InvalidSubnetException: Type[BotocoreClientError]
    InvalidTargetException: Type[BotocoreClientError]
    ListenerNotFoundException: Type[BotocoreClientError]
    LoadBalancerNotFoundException: Type[BotocoreClientError]
    OperationNotPermittedException: Type[BotocoreClientError]
    PriorityInUseException: Type[BotocoreClientError]
    ResourceInUseException: Type[BotocoreClientError]
    RuleNotFoundException: Type[BotocoreClientError]
    SSLPolicyNotFoundException: Type[BotocoreClientError]
    SubnetNotFoundException: Type[BotocoreClientError]
    TargetGroupAssociationLimitException: Type[BotocoreClientError]
    TargetGroupNotFoundException: Type[BotocoreClientError]
    TooManyActionsException: Type[BotocoreClientError]
    TooManyCertificatesException: Type[BotocoreClientError]
    TooManyListenersException: Type[BotocoreClientError]
    TooManyLoadBalancersException: Type[BotocoreClientError]
    TooManyRegistrationsForTargetIdException: Type[BotocoreClientError]
    TooManyRulesException: Type[BotocoreClientError]
    TooManyTagsException: Type[BotocoreClientError]
    TooManyTargetGroupsException: Type[BotocoreClientError]
    TooManyTargetsException: Type[BotocoreClientError]
    TooManyUniqueTargetGroupsPerLoadBalancerException: Type[BotocoreClientError]
    UnsupportedProtocolException: Type[BotocoreClientError]


class ElasticLoadBalancingv2Client(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        ElasticLoadBalancingv2Client exceptions.
        """

    def add_listener_certificates(
        self, *, ListenerArn: str, Certificates: Sequence["CertificateTypeDef"]
    ) -> AddListenerCertificatesOutputTypeDef:
        """
        Adds the specified SSL server certificate to the certificate list for the
        specified HTTPS or TLS listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.add_listener_certificates)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#add_listener_certificates)
        """

    def add_tags(
        self, *, ResourceArns: Sequence[str], Tags: Sequence["TagTypeDef"]
    ) -> Dict[str, Any]:
        """
        Adds the specified tags to the specified Elastic Load Balancing resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.add_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#add_tags)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#can_paginate)
        """

    def create_listener(
        self,
        *,
        LoadBalancerArn: str,
        DefaultActions: Sequence["ActionTypeDef"],
        Protocol: ProtocolEnumType = None,
        Port: int = None,
        SslPolicy: str = None,
        Certificates: Sequence["CertificateTypeDef"] = None,
        AlpnPolicy: Sequence[str] = None,
        Tags: Sequence["TagTypeDef"] = None
    ) -> CreateListenerOutputTypeDef:
        """
        Creates a listener for the specified Application Load Balancer, Network Load
        Balancer, or Gateway Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_listener)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#create_listener)
        """

    def create_load_balancer(
        self,
        *,
        Name: str,
        Subnets: Sequence[str] = None,
        SubnetMappings: Sequence["SubnetMappingTypeDef"] = None,
        SecurityGroups: Sequence[str] = None,
        Scheme: LoadBalancerSchemeEnumType = None,
        Tags: Sequence["TagTypeDef"] = None,
        Type: LoadBalancerTypeEnumType = None,
        IpAddressType: IpAddressTypeType = None,
        CustomerOwnedIpv4Pool: str = None
    ) -> CreateLoadBalancerOutputTypeDef:
        """
        Creates an Application Load Balancer, Network Load Balancer, or Gateway Load
        Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_load_balancer)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#create_load_balancer)
        """

    def create_rule(
        self,
        *,
        ListenerArn: str,
        Conditions: Sequence["RuleConditionTypeDef"],
        Priority: int,
        Actions: Sequence["ActionTypeDef"],
        Tags: Sequence["TagTypeDef"] = None
    ) -> CreateRuleOutputTypeDef:
        """
        Creates a rule for the specified listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_rule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#create_rule)
        """

    def create_target_group(
        self,
        *,
        Name: str,
        Protocol: ProtocolEnumType = None,
        ProtocolVersion: str = None,
        Port: int = None,
        VpcId: str = None,
        HealthCheckProtocol: ProtocolEnumType = None,
        HealthCheckPort: str = None,
        HealthCheckEnabled: bool = None,
        HealthCheckPath: str = None,
        HealthCheckIntervalSeconds: int = None,
        HealthCheckTimeoutSeconds: int = None,
        HealthyThresholdCount: int = None,
        UnhealthyThresholdCount: int = None,
        Matcher: "MatcherTypeDef" = None,
        TargetType: TargetTypeEnumType = None,
        Tags: Sequence["TagTypeDef"] = None
    ) -> CreateTargetGroupOutputTypeDef:
        """
        Creates a target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_target_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#create_target_group)
        """

    def delete_listener(self, *, ListenerArn: str) -> Dict[str, Any]:
        """
        Deletes the specified listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_listener)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#delete_listener)
        """

    def delete_load_balancer(self, *, LoadBalancerArn: str) -> Dict[str, Any]:
        """
        Deletes the specified Application Load Balancer, Network Load Balancer, or
        Gateway Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_load_balancer)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#delete_load_balancer)
        """

    def delete_rule(self, *, RuleArn: str) -> Dict[str, Any]:
        """
        Deletes the specified rule.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_rule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#delete_rule)
        """

    def delete_target_group(self, *, TargetGroupArn: str) -> Dict[str, Any]:
        """
        Deletes the specified target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_target_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#delete_target_group)
        """

    def deregister_targets(
        self, *, TargetGroupArn: str, Targets: Sequence["TargetDescriptionTypeDef"]
    ) -> Dict[str, Any]:
        """
        Deregisters the specified targets from the specified target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.deregister_targets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#deregister_targets)
        """

    def describe_account_limits(
        self, *, Marker: str = None, PageSize: int = None
    ) -> DescribeAccountLimitsOutputTypeDef:
        """
        Describes the current Elastic Load Balancing resource limits for your Amazon Web
        Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_account_limits)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_account_limits)
        """

    def describe_listener_certificates(
        self, *, ListenerArn: str, Marker: str = None, PageSize: int = None
    ) -> DescribeListenerCertificatesOutputTypeDef:
        """
        Describes the default certificate and the certificate list for the specified
        HTTPS or TLS listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_listener_certificates)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_listener_certificates)
        """

    def describe_listeners(
        self,
        *,
        LoadBalancerArn: str = None,
        ListenerArns: Sequence[str] = None,
        Marker: str = None,
        PageSize: int = None
    ) -> DescribeListenersOutputTypeDef:
        """
        Describes the specified listeners or the listeners for the specified Application
        Load Balancer, Network Load Balancer, or Gateway Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_listeners)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_listeners)
        """

    def describe_load_balancer_attributes(
        self, *, LoadBalancerArn: str
    ) -> DescribeLoadBalancerAttributesOutputTypeDef:
        """
        Describes the attributes for the specified Application Load Balancer, Network
        Load Balancer, or Gateway Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_load_balancer_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_load_balancer_attributes)
        """

    def describe_load_balancers(
        self,
        *,
        LoadBalancerArns: Sequence[str] = None,
        Names: Sequence[str] = None,
        Marker: str = None,
        PageSize: int = None
    ) -> DescribeLoadBalancersOutputTypeDef:
        """
        Describes the specified load balancers or all of your load balancers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_load_balancers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_load_balancers)
        """

    def describe_rules(
        self,
        *,
        ListenerArn: str = None,
        RuleArns: Sequence[str] = None,
        Marker: str = None,
        PageSize: int = None
    ) -> DescribeRulesOutputTypeDef:
        """
        Describes the specified rules or the rules for the specified listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_rules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_rules)
        """

    def describe_ssl_policies(
        self, *, Names: Sequence[str] = None, Marker: str = None, PageSize: int = None
    ) -> DescribeSSLPoliciesOutputTypeDef:
        """
        Describes the specified policies or all policies used for SSL negotiation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_ssl_policies)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_ssl_policies)
        """

    def describe_tags(self, *, ResourceArns: Sequence[str]) -> DescribeTagsOutputTypeDef:
        """
        Describes the tags for the specified Elastic Load Balancing resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_tags)
        """

    def describe_target_group_attributes(
        self, *, TargetGroupArn: str
    ) -> DescribeTargetGroupAttributesOutputTypeDef:
        """
        Describes the attributes for the specified target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_target_group_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_target_group_attributes)
        """

    def describe_target_groups(
        self,
        *,
        LoadBalancerArn: str = None,
        TargetGroupArns: Sequence[str] = None,
        Names: Sequence[str] = None,
        Marker: str = None,
        PageSize: int = None
    ) -> DescribeTargetGroupsOutputTypeDef:
        """
        Describes the specified target groups or all of your target groups.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_target_groups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_target_groups)
        """

    def describe_target_health(
        self, *, TargetGroupArn: str, Targets: Sequence["TargetDescriptionTypeDef"] = None
    ) -> DescribeTargetHealthOutputTypeDef:
        """
        Describes the health of the specified targets or all of your targets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_target_health)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#describe_target_health)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = None,
        ExpiresIn: int = 3600,
        HttpMethod: str = None,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#generate_presigned_url)
        """

    def modify_listener(
        self,
        *,
        ListenerArn: str,
        Port: int = None,
        Protocol: ProtocolEnumType = None,
        SslPolicy: str = None,
        Certificates: Sequence["CertificateTypeDef"] = None,
        DefaultActions: Sequence["ActionTypeDef"] = None,
        AlpnPolicy: Sequence[str] = None
    ) -> ModifyListenerOutputTypeDef:
        """
        Replaces the specified properties of the specified listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.modify_listener)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#modify_listener)
        """

    def modify_load_balancer_attributes(
        self, *, LoadBalancerArn: str, Attributes: Sequence["LoadBalancerAttributeTypeDef"]
    ) -> ModifyLoadBalancerAttributesOutputTypeDef:
        """
        Modifies the specified attributes of the specified Application Load Balancer,
        Network Load Balancer, or Gateway Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.modify_load_balancer_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#modify_load_balancer_attributes)
        """

    def modify_rule(
        self,
        *,
        RuleArn: str,
        Conditions: Sequence["RuleConditionTypeDef"] = None,
        Actions: Sequence["ActionTypeDef"] = None
    ) -> ModifyRuleOutputTypeDef:
        """
        Replaces the specified properties of the specified rule.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.modify_rule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#modify_rule)
        """

    def modify_target_group(
        self,
        *,
        TargetGroupArn: str,
        HealthCheckProtocol: ProtocolEnumType = None,
        HealthCheckPort: str = None,
        HealthCheckPath: str = None,
        HealthCheckEnabled: bool = None,
        HealthCheckIntervalSeconds: int = None,
        HealthCheckTimeoutSeconds: int = None,
        HealthyThresholdCount: int = None,
        UnhealthyThresholdCount: int = None,
        Matcher: "MatcherTypeDef" = None
    ) -> ModifyTargetGroupOutputTypeDef:
        """
        Modifies the health checks used when evaluating the health state of the targets
        in the specified target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.modify_target_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#modify_target_group)
        """

    def modify_target_group_attributes(
        self, *, TargetGroupArn: str, Attributes: Sequence["TargetGroupAttributeTypeDef"]
    ) -> ModifyTargetGroupAttributesOutputTypeDef:
        """
        Modifies the specified attributes of the specified target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.modify_target_group_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#modify_target_group_attributes)
        """

    def register_targets(
        self, *, TargetGroupArn: str, Targets: Sequence["TargetDescriptionTypeDef"]
    ) -> Dict[str, Any]:
        """
        Registers the specified targets with the specified target group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.register_targets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#register_targets)
        """

    def remove_listener_certificates(
        self, *, ListenerArn: str, Certificates: Sequence["CertificateTypeDef"]
    ) -> Dict[str, Any]:
        """
        Removes the specified certificate from the certificate list for the specified
        HTTPS or TLS listener.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.remove_listener_certificates)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#remove_listener_certificates)
        """

    def remove_tags(self, *, ResourceArns: Sequence[str], TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes the specified tags from the specified Elastic Load Balancing resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.remove_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#remove_tags)
        """

    def set_ip_address_type(
        self, *, LoadBalancerArn: str, IpAddressType: IpAddressTypeType
    ) -> SetIpAddressTypeOutputTypeDef:
        """
        Sets the type of IP addresses used by the subnets of the specified Application
        Load Balancer or Network Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.set_ip_address_type)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#set_ip_address_type)
        """

    def set_rule_priorities(
        self, *, RulePriorities: Sequence["RulePriorityPairTypeDef"]
    ) -> SetRulePrioritiesOutputTypeDef:
        """
        Sets the priorities of the specified rules.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.set_rule_priorities)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#set_rule_priorities)
        """

    def set_security_groups(
        self, *, LoadBalancerArn: str, SecurityGroups: Sequence[str]
    ) -> SetSecurityGroupsOutputTypeDef:
        """
        Associates the specified security groups with the specified Application Load
        Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.set_security_groups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#set_security_groups)
        """

    def set_subnets(
        self,
        *,
        LoadBalancerArn: str,
        Subnets: Sequence[str] = None,
        SubnetMappings: Sequence["SubnetMappingTypeDef"] = None,
        IpAddressType: IpAddressTypeType = None
    ) -> SetSubnetsOutputTypeDef:
        """
        Enables the Availability Zones for the specified public subnets for the
        specified Application Load Balancer or Network Load Balancer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.set_subnets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/client.html#set_subnets)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_account_limits"]
    ) -> DescribeAccountLimitsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeAccountLimits)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describeaccountlimitspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_listener_certificates"]
    ) -> DescribeListenerCertificatesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeListenerCertificates)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describelistenercertificatespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_listeners"]
    ) -> DescribeListenersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeListeners)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describelistenerspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_load_balancers"]
    ) -> DescribeLoadBalancersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeLoadBalancers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describeloadbalancerspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["describe_rules"]) -> DescribeRulesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeRules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describerulespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_ssl_policies"]
    ) -> DescribeSSLPoliciesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeSSLPolicies)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describesslpoliciespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_target_groups"]
    ) -> DescribeTargetGroupsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Paginator.DescribeTargetGroups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/paginators.html#describetargetgroupspaginator)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["load_balancer_available"]
    ) -> LoadBalancerAvailableWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Waiter.LoadBalancerAvailable)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/waiters.html#loadbalanceravailablewaiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["load_balancer_exists"]) -> LoadBalancerExistsWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Waiter.LoadBalancerExists)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/waiters.html#loadbalancerexistswaiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["load_balancers_deleted"]
    ) -> LoadBalancersDeletedWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Waiter.LoadBalancersDeleted)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/waiters.html#loadbalancersdeletedwaiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["target_deregistered"]) -> TargetDeregisteredWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Waiter.TargetDeregistered)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/waiters.html#targetderegisteredwaiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["target_in_service"]) -> TargetInServiceWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.18.43/reference/services/elbv2.html#ElasticLoadBalancingv2.Waiter.TargetInService)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_elbv2/waiters.html#targetinservicewaiter)
        """
