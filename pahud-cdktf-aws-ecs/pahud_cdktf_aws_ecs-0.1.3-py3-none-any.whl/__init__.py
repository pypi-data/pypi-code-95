'''
[![npm version](https://badge.fury.io/js/@pahud%2Fcdktf-aws-ecs.svg)](https://badge.fury.io/js/@pahud%2Fcdktf-aws-ecs)
[![PyPI version](https://badge.fury.io/py/pahud-cdktf-aws-ecs.svg)](https://badge.fury.io/py/pahud-cdktf-aws-ecs)
[![release](https://github.com/pahud/cdktf-aws-ecs/actions/workflows/release.yml/badge.svg)](https://github.com/pahud/cdktf-aws-ecs/actions/workflows/release.yml)
[![construct hub](https://img.shields.io/badge/Construct%20Hub-available-blue)](https://constructs.dev/packages/@pahud/cdktf-aws-ecs)

# cdktf-aws-ecs

CDKTF construct library for Amazon ECS.

## Usage

The following sample creates:

1. A new VPC
2. Amazon ECS cluster
3. Autoscaling Group capacity provider
4. Autoscaling Group with Launch Template

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from pahud.cdktf_aws_ecs import Cluster

# create the cluster
cluster = Cluster(stack, "EcsCluster")

# create the ASG capacity with capacity provider
cluster.add_asg_capacity("ASGCapacity",
    max_capacity=10,
    min_capacity=0,
    desired_capacity=2
)
```

## Existing VPC subnets

To deploy in any existing VPC, specify the `vpcSubnets.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
cluster.add_asg_capacity("ASGCapacity",
    vpc_subnets=["subnet-111", "subnet-222", "subnet-333"]
)
```
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

import constructs


@jsii.enum(jsii_type="@pahud/cdktf-aws-ecs.AmazonLinuxGeneration")
class AmazonLinuxGeneration(enum.Enum):
    AMAZON_LINUX = "AMAZON_LINUX"
    AMAZON_LINUX_2 = "AMAZON_LINUX_2"


@jsii.enum(jsii_type="@pahud/cdktf-aws-ecs.AmiHardwareType")
class AmiHardwareType(enum.Enum):
    STANDARD = "STANDARD"
    '''Use the standard Amazon ECS-optimized AMI.'''
    GPU = "GPU"
    '''Use the Amazon ECS GPU-optimized AMI.'''
    ARM = "ARM"
    '''Use the Amazon ECS-optimized Amazon Linux 2 (arm64) AMI.'''


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-ecs.AsgCapacityOptions",
    jsii_struct_bases=[],
    name_mapping={
        "desired_capacity": "desiredCapacity",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
    },
)
class AsgCapacityOptions:
    def __init__(
        self,
        *,
        desired_capacity: typing.Optional[jsii.Number] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param desired_capacity: 
        :param max_capacity: 
        :param min_capacity: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AsgCapacityOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Cluster(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-ecs.Cluster",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: typing.Optional["ClusterProps"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAsgCapacity")
    def add_asg_capacity(
        self,
        id: builtins.str,
        *,
        desired_capacity: typing.Optional[jsii.Number] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: -
        :param desired_capacity: 
        :param max_capacity: 
        :param min_capacity: 
        '''
        options = AsgCapacityOptions(
            desired_capacity=desired_capacity,
            max_capacity=max_capacity,
            min_capacity=min_capacity,
        )

        return typing.cast(None, jsii.invoke(self, "addAsgCapacity", [id, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcId"))


class ClusterProps(
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-ecs.ClusterProps",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[builtins.str]:
        '''instance type for the default capacity.

        :default: t3.large
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region to deploy.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''VPC subnet IDs for the container instances.

        :default: - private subnets of a new VPC.
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSubnets"))


class EcsOptimizedAmi(
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-ecs.EcsOptimizedAmi",
):
    def __init__(
        self,
        scope: constructs.Construct,
        *,
        generation: typing.Optional[AmazonLinuxGeneration] = None,
        hwtype: typing.Optional[AmiHardwareType] = None,
    ) -> None:
        '''
        :param scope: -
        :param generation: 
        :param hwtype: 
        '''
        props = EcsOptimizedAmiProps(generation=generation, hwtype=hwtype)

        jsii.create(self.__class__, self, [scope, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiId")
    def ami_id(self) -> builtins.str:
        '''Return the correct image.'''
        return typing.cast(builtins.str, jsii.get(self, "amiId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiParameterName")
    def ami_parameter_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amiParameterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generation")
    def generation(self) -> AmazonLinuxGeneration:
        return typing.cast(AmazonLinuxGeneration, jsii.get(self, "generation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hwType")
    def hw_type(self) -> AmiHardwareType:
        return typing.cast(AmiHardwareType, jsii.get(self, "hwType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> constructs.Construct:
        return typing.cast(constructs.Construct, jsii.get(self, "scope"))


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-ecs.EcsOptimizedAmiProps",
    jsii_struct_bases=[],
    name_mapping={"generation": "generation", "hwtype": "hwtype"},
)
class EcsOptimizedAmiProps:
    def __init__(
        self,
        *,
        generation: typing.Optional[AmazonLinuxGeneration] = None,
        hwtype: typing.Optional[AmiHardwareType] = None,
    ) -> None:
        '''
        :param generation: 
        :param hwtype: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if generation is not None:
            self._values["generation"] = generation
        if hwtype is not None:
            self._values["hwtype"] = hwtype

    @builtins.property
    def generation(self) -> typing.Optional[AmazonLinuxGeneration]:
        result = self._values.get("generation")
        return typing.cast(typing.Optional[AmazonLinuxGeneration], result)

    @builtins.property
    def hwtype(self) -> typing.Optional[AmiHardwareType]:
        result = self._values.get("hwtype")
        return typing.cast(typing.Optional[AmiHardwareType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsOptimizedAmiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StringParameter(
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-ecs.StringParameter",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="valueFromLookup") # type: ignore[misc]
    @builtins.classmethod
    def value_from_lookup(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        parameter_name: builtins.str,
    ) -> builtins.str:
        '''
        :param scope: -
        :param id: -
        :param parameter_name: -
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "valueFromLookup", [scope, id, parameter_name]))


__all__ = [
    "AmazonLinuxGeneration",
    "AmiHardwareType",
    "AsgCapacityOptions",
    "Cluster",
    "ClusterProps",
    "EcsOptimizedAmi",
    "EcsOptimizedAmiProps",
    "StringParameter",
]

publication.publish()
