'''
# serverless-container-constructs

CDK patterns for modern application with serverless containers on AWS

# `AlbFargateServices`

Inspired by *Vijay Menon* from the [AWS blog post](https://aws.amazon.com/blogs/containers/how-to-use-multiple-load-balancer-target-group-support-for-amazon-ecs-to-access-internal-and-external-service-endpoint-using-the-same-dns-name/) introduced in 2019, `AlbFargateServices` allows you to create one or many fargate services with both internet-facing ALB and internal ALB associated with all services. With this pattern, fargate services will be allowed to intercommunicat via internal ALB while external inbound traffic will be spread across the same service tasks through internet-facing ALB.

The sample below will create 3 fargate services associated with both external and internal ALBs. The internal ALB will have an alias(`internal.svc.local`) auto-configured from Route 53 so services can communite through the private ALB endpoint.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from serverless_container_constructs import AlbFargateServices

AlbFargateServices(stack, "Service",
    spot=True, # FARGATE_SPOT only cluster
    tasks=[{
        "listener_port": 80,
        "task": order_task,
        "desired_count": 2,
        # customize the service autoscaling policy
        "scaling_policy": {
            "max_capacity": 20,
            "request_per_target": 1000,
            "target_cpu_utilization": 50
        }
    }, {"listener_port": 8080, "task": customer_task, "desired_count": 2}, {"listener_port": 9090, "task": product_task, "desired_count": 2}
    ],
    route53_ops={
        "zone_name": zone_name, # svc.local
        "external_alb_record_name": external_alb_record_name, # external.svc.local
        "internal_alb_record_name": internal_alb_record_name
    }
)
```

## Fargate Spot Support

By enabling the `spot` property, 100% fargate spot tasks will be provisioned to help you save up to 70%. Check more details about [Fargate Spot](https://aws.amazon.com/about-aws/whats-new/2019/12/aws-launches-fargate-spot-save-up-to-70-for-fault-tolerant-applications/?nc1=h_ls). This is a handy catch-all flag to force all tasks to be `FARGATE_SPOT` only.

To specify mixed strategy with partial `FARGATE` and partial `FARGATE_SPOT`, specify the `capacityProviderStrategy` for individual tasks like

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
AlbFargateServices(stack, "Service",
    tasks=[{
        "listener_port": 8080,
        "task": customer_task,
        "desired_count": 2,
        "capacity_provider_strategy": [{
            "capacity_provider": "FARGATE",
            "base": 1,
            "weight": 1
        }, {
            "capacity_provider": "FARGATE_SPOT",
            "base": 0,
            "weight": 3
        }
        ]
    }
    ]
)
```

The custom capacity provider strategy will be applied if `capacityProviderStretegy` is specified, otherwise, 100% spot will be used when `spot: true`. The default policy is 100% Fargate on-demand.

## ECS Exec

Simply turn on the `enableExecuteCommand` property to enable the [ECS Exec](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html) support for all services.

## Internal or External Only

By default, all task(s) defined in the `AlbFargateServices` will be registered to both external and internal ALBs.
Set `accessibility` to make it internal only, external only, or both.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
AlbFargateServices(stack, "Service",
    tasks=[{"listener_port": 8080, "task": task1, "accessibility": LoadBalancerAccessibility.INTERNAL_ONLY}, {"listener_port": 8081, "task": task2, "accessibility": LoadBalancerAccessibility.EXTERNAL_ONLY}, {"listener_port": 8082, "task": task3}
    ]
)
```

Please note if all tasks are defined as `INTERNAL_ONLY`, no external ALB will be created. Similarly, no internal ALB
will be created if all defined as `EXTERNAL_ONLY`.

## VPC Subnets

By default, all tasks will be deployed in the private subnets. You will need the NAT gateway for the default route associated with the private subnets to ensure the task can successfully pull the container images.

However, you are allowed to specify `vpcSubnets` to customize the subnet selection.

To deploy all tasks in public subnets, one per AZ:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
AlbFargateServices(stack, "Service",
    vpc_subnets={
        "subnet_type": ec2.SubnetType.PUBLIC,
        "one_per_az": True
    }, ...
)
```

This will implicitly enable the `auto assign public IP` for each fargate task so the task can successfully pull the container images from external registry. However, the ingress traffic will still be balanced via the external ALB.

To deploy all tasks in specific subnets:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
AlbFargateServices(stack, "Service",
    vpc_subnets={
        "subnets": [
            ec2.Subnet.from_subnet_id(stack, "sub-1a", "subnet-0e9460dbcfc4cf6ee"),
            ec2.Subnet.from_subnet_id(stack, "sub-1b", "subnet-0562f666bdf5c29af"),
            ec2.Subnet.from_subnet_id(stack, "sub-1c", "subnet-00ab15c0022872f06")
        ]
    }, ...
)
```

## Sample Application

This repository comes with a sample applicaiton with 3 services in Golang. On deployment, the `Order` service will be exposed externally on external ALB port `80` and all requests to the `Order` service will trigger sub-requests internally to another other two services(`product` and `customer`) through the internal ALB and eventually aggregate the response back to the client.

![](images/AlbFargateServices.svg)

## Deploy

To deploy the sample application in you default VPC:

```sh
// install first
yarn install
npx cdk diff -c use_default_vpc=1
npx cdk deploy -c use_default_vpc=1
```

On deployment complete, you will see the external ALB endpoint in the CDK output. `cURL` the external HTTP endpoint and you should be able to see the aggregated response.

```sh
$ curl http://demo-Servi-EH1OINYDWDU9-1397122594.ap-northeast-1.elb.amazonaws.com

{"service":"order", "version":"1.0"}
{"service":"product","version":"1.0"}
{"service":"customer","version":"1.0"}
```

## `cdk-nag` with `AwsSolutions` check

This construct follows the best practices from the [AWS Solutoins](https://github.com/cdklabs/cdk-nag/blob/main/RULES.md#awssolutions) with [cdk-nag](https://github.com/cdklabs/cdk-nag). Enable the `AWS_SOLUTIONS_CHECK` context variable to check aginst the cdk-nag rules.

```sh
npx cdk diff -c AWS_SOLUTIONS_CHECK=1
or
npx cdk synth -c AWS_SOLUTIONS_CHECK=1
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.core


class BaseFargateServices(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="serverless-container-constructs.BaseFargateServices",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param tasks: 
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        props = BaseFargateServicesProps(
            tasks=tasks,
            enable_execute_command=enable_execute_command,
            route53_ops=route53_ops,
            spot=spot,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> typing.List[aws_cdk.aws_ecs.FargateService]:
        '''The service(s) created from the task(s).'''
        return typing.cast(typing.List[aws_cdk.aws_ecs.FargateService], jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasExternalLoadBalancer")
    def _has_external_load_balancer(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasExternalLoadBalancer"))

    @_has_external_load_balancer.setter
    def _has_external_load_balancer(self, value: builtins.bool) -> None:
        jsii.set(self, "hasExternalLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasInternalLoadBalancer")
    def _has_internal_load_balancer(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasInternalLoadBalancer"))

    @_has_internal_load_balancer.setter
    def _has_internal_load_balancer(self, value: builtins.bool) -> None:
        jsii.set(self, "hasInternalLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def _vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, jsii.get(self, "vpcSubnets"))

    @_vpc_subnets.setter
    def _vpc_subnets(self, value: aws_cdk.aws_ec2.SubnetSelection) -> None:
        jsii.set(self, "vpcSubnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneName")
    def _zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @_zone_name.setter
    def _zone_name(self, value: builtins.str) -> None:
        jsii.set(self, "zoneName", value)


class _BaseFargateServicesProxy(BaseFargateServices):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseFargateServices).__jsii_proxy_class__ = lambda : _BaseFargateServicesProxy


@jsii.data_type(
    jsii_type="serverless-container-constructs.BaseFargateServicesProps",
    jsii_struct_bases=[],
    name_mapping={
        "tasks": "tasks",
        "enable_execute_command": "enableExecuteCommand",
        "route53_ops": "route53Ops",
        "spot": "spot",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class BaseFargateServicesProps:
    def __init__(
        self,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param tasks: 
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        if isinstance(route53_ops, dict):
            route53_ops = Route53Options(**route53_ops)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "tasks": tasks,
        }
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if route53_ops is not None:
            self._values["route53_ops"] = route53_ops
        if spot is not None:
            self._values["spot"] = spot
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def tasks(self) -> typing.List["FargateTaskProps"]:
        result = self._values.get("tasks")
        assert result is not None, "Required property 'tasks' is missing"
        return typing.cast(typing.List["FargateTaskProps"], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable ECS Exec support.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def route53_ops(self) -> typing.Optional["Route53Options"]:
        result = self._values.get("route53_ops")
        return typing.cast(typing.Optional["Route53Options"], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''create a FARGATE_SPOT only cluster.

        :default: false
        '''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnets to associate with the service.

        :default:

        -

        {
        subnetType: ec2.SubnetType.PRIVATE,
        }
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseFargateServicesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="serverless-container-constructs.FargateTaskProps",
    jsii_struct_bases=[],
    name_mapping={
        "listener_port": "listenerPort",
        "task": "task",
        "accessibility": "accessibility",
        "capacity_provider_strategy": "capacityProviderStrategy",
        "desired_count": "desiredCount",
        "scaling_policy": "scalingPolicy",
    },
)
class FargateTaskProps:
    def __init__(
        self,
        *,
        listener_port: jsii.Number,
        task: aws_cdk.aws_ecs.FargateTaskDefinition,
        accessibility: typing.Optional["LoadBalancerAccessibility"] = None,
        capacity_provider_strategy: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.CapacityProviderStrategy]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        scaling_policy: typing.Optional["ServiceScalingPolicy"] = None,
    ) -> None:
        '''
        :param listener_port: 
        :param task: 
        :param accessibility: Register the service to internal ELB, external ELB or both. Default: both
        :param capacity_provider_strategy: 
        :param desired_count: desired number of tasks for the service. Default: 1
        :param scaling_policy: service autoscaling policy. Default: - { maxCapacity: 10, targetCpuUtilization: 50, requestsPerTarget: 1000 }
        '''
        if isinstance(scaling_policy, dict):
            scaling_policy = ServiceScalingPolicy(**scaling_policy)
        self._values: typing.Dict[str, typing.Any] = {
            "listener_port": listener_port,
            "task": task,
        }
        if accessibility is not None:
            self._values["accessibility"] = accessibility
        if capacity_provider_strategy is not None:
            self._values["capacity_provider_strategy"] = capacity_provider_strategy
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if scaling_policy is not None:
            self._values["scaling_policy"] = scaling_policy

    @builtins.property
    def listener_port(self) -> jsii.Number:
        result = self._values.get("listener_port")
        assert result is not None, "Required property 'listener_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def task(self) -> aws_cdk.aws_ecs.FargateTaskDefinition:
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(aws_cdk.aws_ecs.FargateTaskDefinition, result)

    @builtins.property
    def accessibility(self) -> typing.Optional["LoadBalancerAccessibility"]:
        '''Register the service to internal ELB, external ELB or both.

        :default: both
        '''
        result = self._values.get("accessibility")
        return typing.cast(typing.Optional["LoadBalancerAccessibility"], result)

    @builtins.property
    def capacity_provider_strategy(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ecs.CapacityProviderStrategy]]:
        result = self._values.get("capacity_provider_strategy")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.CapacityProviderStrategy]], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''desired number of tasks for the service.

        :default: 1
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scaling_policy(self) -> typing.Optional["ServiceScalingPolicy"]:
        '''service autoscaling policy.

        :default: - { maxCapacity: 10, targetCpuUtilization: 50, requestsPerTarget: 1000 }
        '''
        result = self._values.get("scaling_policy")
        return typing.cast(typing.Optional["ServiceScalingPolicy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="serverless-container-constructs.LoadBalancerAccessibility")
class LoadBalancerAccessibility(enum.Enum):
    '''The load balancer accessibility.'''

    EXTERNAL_ONLY = "EXTERNAL_ONLY"
    '''register to external load balancer only.'''
    INTERNAL_ONLY = "INTERNAL_ONLY"
    '''register to internal load balancer only.'''


@jsii.data_type(
    jsii_type="serverless-container-constructs.Route53Options",
    jsii_struct_bases=[],
    name_mapping={
        "external_elb_record_name": "externalElbRecordName",
        "internal_elb_record_name": "internalElbRecordName",
        "zone_name": "zoneName",
    },
)
class Route53Options:
    def __init__(
        self,
        *,
        external_elb_record_name: typing.Optional[builtins.str] = None,
        internal_elb_record_name: typing.Optional[builtins.str] = None,
        zone_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param external_elb_record_name: the external ELB record name. Default: external
        :param internal_elb_record_name: the internal ELB record name. Default: internal
        :param zone_name: private zone name. Default: svc.local
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if external_elb_record_name is not None:
            self._values["external_elb_record_name"] = external_elb_record_name
        if internal_elb_record_name is not None:
            self._values["internal_elb_record_name"] = internal_elb_record_name
        if zone_name is not None:
            self._values["zone_name"] = zone_name

    @builtins.property
    def external_elb_record_name(self) -> typing.Optional[builtins.str]:
        '''the external ELB record name.

        :default: external
        '''
        result = self._values.get("external_elb_record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def internal_elb_record_name(self) -> typing.Optional[builtins.str]:
        '''the internal ELB record name.

        :default: internal
        '''
        result = self._values.get("internal_elb_record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_name(self) -> typing.Optional[builtins.str]:
        '''private zone name.

        :default: svc.local
        '''
        result = self._values.get("zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Route53Options(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="serverless-container-constructs.ServiceScalingPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "max_capacity": "maxCapacity",
        "request_per_target": "requestPerTarget",
        "target_cpu_utilization": "targetCpuUtilization",
    },
)
class ServiceScalingPolicy:
    def __init__(
        self,
        *,
        max_capacity: typing.Optional[jsii.Number] = None,
        request_per_target: typing.Optional[jsii.Number] = None,
        target_cpu_utilization: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_capacity: max capacity for the service autoscaling. Default: 10
        :param request_per_target: request per target. Default: 1000
        :param target_cpu_utilization: target cpu utilization. Default: 50
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if request_per_target is not None:
            self._values["request_per_target"] = request_per_target
        if target_cpu_utilization is not None:
            self._values["target_cpu_utilization"] = target_cpu_utilization

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''max capacity for the service autoscaling.

        :default: 10
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def request_per_target(self) -> typing.Optional[jsii.Number]:
        '''request per target.

        :default: 1000
        '''
        result = self._values.get("request_per_target")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_cpu_utilization(self) -> typing.Optional[jsii.Number]:
        '''target cpu utilization.

        :default: 50
        '''
        result = self._values.get("target_cpu_utilization")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceScalingPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlbFargateServices(
    BaseFargateServices,
    metaclass=jsii.JSIIMeta,
    jsii_type="serverless-container-constructs.AlbFargateServices",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        tasks: typing.Sequence[FargateTaskProps],
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional[Route53Options] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param tasks: 
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        props = AlbFargateServicesProps(
            tasks=tasks,
            enable_execute_command=enable_execute_command,
            route53_ops=route53_ops,
            spot=spot,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalAlb")
    def external_alb(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], jsii.get(self, "externalAlb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalAlb")
    def internal_alb(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], jsii.get(self, "internalAlb"))


@jsii.data_type(
    jsii_type="serverless-container-constructs.AlbFargateServicesProps",
    jsii_struct_bases=[BaseFargateServicesProps],
    name_mapping={
        "tasks": "tasks",
        "enable_execute_command": "enableExecuteCommand",
        "route53_ops": "route53Ops",
        "spot": "spot",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class AlbFargateServicesProps(BaseFargateServicesProps):
    def __init__(
        self,
        *,
        tasks: typing.Sequence[FargateTaskProps],
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional[Route53Options] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param tasks: 
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        if isinstance(route53_ops, dict):
            route53_ops = Route53Options(**route53_ops)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "tasks": tasks,
        }
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if route53_ops is not None:
            self._values["route53_ops"] = route53_ops
        if spot is not None:
            self._values["spot"] = spot
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def tasks(self) -> typing.List[FargateTaskProps]:
        result = self._values.get("tasks")
        assert result is not None, "Required property 'tasks' is missing"
        return typing.cast(typing.List[FargateTaskProps], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable ECS Exec support.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def route53_ops(self) -> typing.Optional[Route53Options]:
        result = self._values.get("route53_ops")
        return typing.cast(typing.Optional[Route53Options], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''create a FARGATE_SPOT only cluster.

        :default: false
        '''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnets to associate with the service.

        :default:

        -

        {
        subnetType: ec2.SubnetType.PRIVATE,
        }
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbFargateServicesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlbFargateServices",
    "AlbFargateServicesProps",
    "BaseFargateServices",
    "BaseFargateServicesProps",
    "FargateTaskProps",
    "LoadBalancerAccessibility",
    "Route53Options",
    "ServiceScalingPolicy",
]

publication.publish()
