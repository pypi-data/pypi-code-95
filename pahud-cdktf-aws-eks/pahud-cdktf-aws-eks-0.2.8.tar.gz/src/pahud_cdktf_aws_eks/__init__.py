'''
[![npm version](https://badge.fury.io/js/@pahud%2Fcdktf-aws-eks.svg)](https://badge.fury.io/js/@pahud%2Fcdktf-aws-eks)
[![PyPI version](https://badge.fury.io/py/pahud-cdktf-aws-eks.svg)](https://badge.fury.io/py/pahud-cdktf-aws-eks)
[![release](https://github.com/pahud/cdktf-aws-eks/actions/workflows/release.yml/badge.svg)](https://github.com/pahud/cdktf-aws-eks/actions/workflows/release.yml)
[![construct hub](https://img.shields.io/badge/Construct%20Hub-available-blue)](https://constructs.dev/packages/@pahud/cdktf-aws-eks)

# cdktf-aws-eks

CDKTF construct library for Amazon EKS.

## Usage

The following sample creates:

1. A new VPC
2. Amazon EKS cluster(control plane)
3. The default nodegroup with the cluster
4. The 2nd nodegroup with spot instances

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from pahud.cdktf_aws_eks import Cluster

# create the cluster and the default nodegroup
cluster = Cluster(stack, "demo-cluster",
    version=KubernetesVersion.V1_21,
    scaling_config={"min_capacity": 1}
)

# create the optional 2nd nodegroup
cluster.add_node_group("NG2",
    scaling_config={
        "min_capacity": 1,
        "max_capacity": 10,
        "desired_capacity": 5
    },
    capacity_type=CapacityType.SPOT,
    instance_types=["t3.large", "c5.large", "m5.large"]
)
```

## Existing VPC subnets

To deploy in any existing VPC, specify the `privateSubnets` and `publicSubnets`(if any).

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
Cluster(stack, "demo-cluster",
    private_subnets=["subnet-111", "subnet-222", "subnet-333"],
    public_subnets=["subnet-444", "subnet-555", "subnet-666"],
    version=KubernetesVersion.V1_21
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

import cdktf
import cdktf_cdktf_provider_aws
import constructs


@jsii.enum(jsii_type="@pahud/cdktf-aws-eks.CapacityType")
class CapacityType(enum.Enum):
    SPOT = "SPOT"
    ON_DEMAND = "ON_DEMAND"


class Cluster(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-eks.Cluster",
):
    '''The Amazon EKS Cluster with a default nodegroup.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        version: "KubernetesVersion",
        capacity_type: typing.Optional[CapacityType] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        private_subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        public_subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        region: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param version: Kubernetes cluster version.
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param cluster_name: The Amazon EKS cluster name.
        :param instance_types: instance types of the default nodegroup. Default: ['t3.large']
        :param private_subnets: list of private subnetIds for an existing VPC.
        :param public_subnets: list of public subnetIds for an existing VPC.
        :param region: The AWS region to deploy.
        :param scaling_config: The scaling config of the default nodegroup.
        '''
        props = ClusterProps(
            version=version,
            capacity_type=capacity_type,
            cluster_name=cluster_name,
            instance_types=instance_types,
            private_subnets=private_subnets,
            public_subnets=public_subnets,
            region=region,
            scaling_config=scaling_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addNodeGroup")
    def add_node_group(
        self,
        id: builtins.str,
        *,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        capacity_type: typing.Optional[CapacityType] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_role: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
    ) -> None:
        '''
        :param id: -
        :param subnets: subnet IDs for the nodegroup.
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param depends_on: resources to depend on;
        :param instance_types: instance types of the nodegroup. Default: ['t3.large']
        :param node_role: nodegroup role arn. Default: - The IAM role for the default nodegroup.
        :param scaling_config: scaling configuration for the nodegroup.
        '''
        options = NodeGroupOptions(
            subnets=subnets,
            capacity_type=capacity_type,
            depends_on=depends_on,
            instance_types=instance_types,
            node_role=node_role,
            scaling_config=scaling_config,
        )

        return typing.cast(None, jsii.invoke(self, "addNodeGroup", [id, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> cdktf_cdktf_provider_aws.EksCluster:
        return typing.cast(cdktf_cdktf_provider_aws.EksCluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "privateSubnets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "ClusterProps":
        return typing.cast("ClusterProps", jsii.get(self, "props"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "publicSubnets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultNodeGroup")
    def default_node_group(self) -> typing.Optional["NodeGroup"]:
        return typing.cast(typing.Optional["NodeGroup"], jsii.get(self, "defaultNodeGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcId"))


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-eks.ClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "version": "version",
        "capacity_type": "capacityType",
        "cluster_name": "clusterName",
        "instance_types": "instanceTypes",
        "private_subnets": "privateSubnets",
        "public_subnets": "publicSubnets",
        "region": "region",
        "scaling_config": "scalingConfig",
    },
)
class ClusterProps:
    def __init__(
        self,
        *,
        version: "KubernetesVersion",
        capacity_type: typing.Optional[CapacityType] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        private_subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        public_subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        region: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
    ) -> None:
        '''Properties for the Cluster.

        :param version: Kubernetes cluster version.
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param cluster_name: The Amazon EKS cluster name.
        :param instance_types: instance types of the default nodegroup. Default: ['t3.large']
        :param private_subnets: list of private subnetIds for an existing VPC.
        :param public_subnets: list of public subnetIds for an existing VPC.
        :param region: The AWS region to deploy.
        :param scaling_config: The scaling config of the default nodegroup.
        '''
        if isinstance(scaling_config, dict):
            scaling_config = ScalingConfig(**scaling_config)
        self._values: typing.Dict[str, typing.Any] = {
            "version": version,
        }
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if private_subnets is not None:
            self._values["private_subnets"] = private_subnets
        if public_subnets is not None:
            self._values["public_subnets"] = public_subnets
        if region is not None:
            self._values["region"] = region
        if scaling_config is not None:
            self._values["scaling_config"] = scaling_config

    @builtins.property
    def version(self) -> "KubernetesVersion":
        '''Kubernetes cluster version.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast("KubernetesVersion", result)

    @builtins.property
    def capacity_type(self) -> typing.Optional[CapacityType]:
        '''capacity type of the nodegroup.

        :default: CapacityType.ON_DEMAND
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[CapacityType], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''The Amazon EKS cluster name.'''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''instance types of the default nodegroup.

        :default: ['t3.large']
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def private_subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''list of private subnetIds for an existing VPC.'''
        result = self._values.get("private_subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def public_subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''list of public subnetIds for an existing VPC.'''
        result = self._values.get("public_subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region to deploy.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scaling_config(self) -> typing.Optional["ScalingConfig"]:
        '''The scaling config of the default nodegroup.'''
        result = self._values.get("scaling_config")
        return typing.cast(typing.Optional["ScalingConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-eks.KubernetesVersion",
):
    '''Kubernetes cluster version.'''

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, version: builtins.str) -> "KubernetesVersion":
        '''Custom cluster version.

        :param version: custom version number.
        '''
        return typing.cast("KubernetesVersion", jsii.sinvoke(cls, "of", [version]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_14")
    def V1_14(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.14.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_14"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_15")
    def V1_15(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.15.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_15"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_16")
    def V1_16(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.16.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_16"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_17")
    def V1_17(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.17.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_17"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_18")
    def V1_18(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.18.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_18"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_19")
    def V1_19(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.19.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_19"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_20")
    def V1_20(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.20.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_20"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_21")
    def V1_21(cls) -> "KubernetesVersion":
        '''Kubernetes version 1.21.'''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_21"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''cluster version number.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class NodeGroup(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pahud/cdktf-aws-eks.NodeGroup",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        subnets: typing.Sequence[builtins.str],
        capacity_type: typing.Optional[CapacityType] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_role: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_name: cluster name.
        :param subnets: subnet IDs for the nodegroup.
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param depends_on: resources to depend on;
        :param instance_types: instance types of the nodegroup. Default: ['t3.large']
        :param node_role: nodegroup role arn. Default: - The IAM role for the default nodegroup.
        :param scaling_config: scaling configuration for the nodegroup.
        '''
        props = NodeGroupProps(
            cluster_name=cluster_name,
            subnets=subnets,
            capacity_type=capacity_type,
            depends_on=depends_on,
            instance_types=instance_types,
            node_role=node_role,
            scaling_config=scaling_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeGroupRoleArn")
    def node_group_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeGroupRoleArn"))


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-eks.NodeGroupBaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "capacity_type": "capacityType",
        "depends_on": "dependsOn",
        "instance_types": "instanceTypes",
        "node_role": "nodeRole",
        "scaling_config": "scalingConfig",
    },
)
class NodeGroupBaseOptions:
    def __init__(
        self,
        *,
        capacity_type: typing.Optional[CapacityType] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_role: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
    ) -> None:
        '''
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param depends_on: resources to depend on;
        :param instance_types: instance types of the nodegroup. Default: ['t3.large']
        :param node_role: nodegroup role arn. Default: - The IAM role for the default nodegroup.
        :param scaling_config: scaling configuration for the nodegroup.
        '''
        if isinstance(scaling_config, dict):
            scaling_config = ScalingConfig(**scaling_config)
        self._values: typing.Dict[str, typing.Any] = {}
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if node_role is not None:
            self._values["node_role"] = node_role
        if scaling_config is not None:
            self._values["scaling_config"] = scaling_config

    @builtins.property
    def capacity_type(self) -> typing.Optional[CapacityType]:
        '''capacity type of the nodegroup.

        :default: CapacityType.ON_DEMAND
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[CapacityType], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''resources to depend on;'''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''instance types of the nodegroup.

        :default: ['t3.large']
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node_role(self) -> typing.Optional[builtins.str]:
        '''nodegroup role arn.

        :default: - The IAM role for the default nodegroup.
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scaling_config(self) -> typing.Optional["ScalingConfig"]:
        '''scaling configuration for the nodegroup.

        :see: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_node_group#scaling_config-configuration-block
        '''
        result = self._values.get("scaling_config")
        return typing.cast(typing.Optional["ScalingConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodeGroupBaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-eks.NodeGroupOptions",
    jsii_struct_bases=[NodeGroupBaseOptions],
    name_mapping={
        "capacity_type": "capacityType",
        "depends_on": "dependsOn",
        "instance_types": "instanceTypes",
        "node_role": "nodeRole",
        "scaling_config": "scalingConfig",
        "subnets": "subnets",
    },
)
class NodeGroupOptions(NodeGroupBaseOptions):
    def __init__(
        self,
        *,
        capacity_type: typing.Optional[CapacityType] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_role: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param depends_on: resources to depend on;
        :param instance_types: instance types of the nodegroup. Default: ['t3.large']
        :param node_role: nodegroup role arn. Default: - The IAM role for the default nodegroup.
        :param scaling_config: scaling configuration for the nodegroup.
        :param subnets: subnet IDs for the nodegroup.
        '''
        if isinstance(scaling_config, dict):
            scaling_config = ScalingConfig(**scaling_config)
        self._values: typing.Dict[str, typing.Any] = {}
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if node_role is not None:
            self._values["node_role"] = node_role
        if scaling_config is not None:
            self._values["scaling_config"] = scaling_config
        if subnets is not None:
            self._values["subnets"] = subnets

    @builtins.property
    def capacity_type(self) -> typing.Optional[CapacityType]:
        '''capacity type of the nodegroup.

        :default: CapacityType.ON_DEMAND
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[CapacityType], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''resources to depend on;'''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''instance types of the nodegroup.

        :default: ['t3.large']
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node_role(self) -> typing.Optional[builtins.str]:
        '''nodegroup role arn.

        :default: - The IAM role for the default nodegroup.
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scaling_config(self) -> typing.Optional["ScalingConfig"]:
        '''scaling configuration for the nodegroup.

        :see: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_node_group#scaling_config-configuration-block
        '''
        result = self._values.get("scaling_config")
        return typing.cast(typing.Optional["ScalingConfig"], result)

    @builtins.property
    def subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''subnet IDs for the nodegroup.'''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodeGroupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-eks.NodeGroupProps",
    jsii_struct_bases=[NodeGroupBaseOptions],
    name_mapping={
        "capacity_type": "capacityType",
        "depends_on": "dependsOn",
        "instance_types": "instanceTypes",
        "node_role": "nodeRole",
        "scaling_config": "scalingConfig",
        "cluster_name": "clusterName",
        "subnets": "subnets",
    },
)
class NodeGroupProps(NodeGroupBaseOptions):
    def __init__(
        self,
        *,
        capacity_type: typing.Optional[CapacityType] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_role: typing.Optional[builtins.str] = None,
        scaling_config: typing.Optional["ScalingConfig"] = None,
        cluster_name: builtins.str,
        subnets: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param capacity_type: capacity type of the nodegroup. Default: CapacityType.ON_DEMAND
        :param depends_on: resources to depend on;
        :param instance_types: instance types of the nodegroup. Default: ['t3.large']
        :param node_role: nodegroup role arn. Default: - The IAM role for the default nodegroup.
        :param scaling_config: scaling configuration for the nodegroup.
        :param cluster_name: cluster name.
        :param subnets: subnet IDs for the nodegroup.
        '''
        if isinstance(scaling_config, dict):
            scaling_config = ScalingConfig(**scaling_config)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
            "subnets": subnets,
        }
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if node_role is not None:
            self._values["node_role"] = node_role
        if scaling_config is not None:
            self._values["scaling_config"] = scaling_config

    @builtins.property
    def capacity_type(self) -> typing.Optional[CapacityType]:
        '''capacity type of the nodegroup.

        :default: CapacityType.ON_DEMAND
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[CapacityType], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''resources to depend on;'''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''instance types of the nodegroup.

        :default: ['t3.large']
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node_role(self) -> typing.Optional[builtins.str]:
        '''nodegroup role arn.

        :default: - The IAM role for the default nodegroup.
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scaling_config(self) -> typing.Optional["ScalingConfig"]:
        '''scaling configuration for the nodegroup.

        :see: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_node_group#scaling_config-configuration-block
        '''
        result = self._values.get("scaling_config")
        return typing.cast(typing.Optional["ScalingConfig"], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''cluster name.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnets(self) -> typing.List[builtins.str]:
        '''subnet IDs for the nodegroup.'''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodeGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pahud/cdktf-aws-eks.ScalingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "desired_capacity": "desiredCapacity",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
    },
)
class ScalingConfig:
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
        return "ScalingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CapacityType",
    "Cluster",
    "ClusterProps",
    "KubernetesVersion",
    "NodeGroup",
    "NodeGroupBaseOptions",
    "NodeGroupOptions",
    "NodeGroupProps",
    "ScalingConfig",
]

publication.publish()
