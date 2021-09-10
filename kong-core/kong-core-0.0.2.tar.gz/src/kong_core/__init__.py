'''
# kong-control-plane

[![NPM version](https://badge.fury.io/js/kong-core.svg)](https://badge.fury.io/js/kong-core)
[![PyPI version](https://badge.fury.io/py/kong-core.svg)](https://badge.fury.io/py/kong-core)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/kong-control-plane?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/kong-control-plane?label=pypi&color=blue)

Use this Kong CDK Construct Library to deploy Core common infrastructural constructs .

This CDK library automatically creates and configures recommended architecture on AWS by:

* *Amazon EKS*

  * Well architected EKS cluster from networking standpoint
  * Cluster autoscaler
  * Node termination handler
  * Secrets management from AWS Secrets Manager using CSI driver
  * mTLS using AWS ACM for pod to pod communication using private certificate authority and aws-pca-issuer
  * Use of IAM Role for Service Account (IRSA) where applicable
  * AWS EKS encryption at rest
  * Metrics server installation
  * Logs and metrics to cloudwatch using AWS CloudWatch Container insights
* *Elasticache*

  * private accessibility
  * multi az
  * auto failover
  * auto minor version upgrade
  * cwl output
* *RDS Features*

  * Encryption at rest
  * Private subnets
  * Multiaz
  * auto backup
  * Logs output to CloudWatch

## npm Package Installation:

```
yarn add --dev kong-core
# or
npm install kong-core --save-dev
```

## PyPI Package Installation:

```
pip install kong-core
```

# Sample

Try out https://github.com/kong/aws-samples for the complete sample application and instructions.

## Resources to learn about CDK

* [CDK TypeScript Workshop](https://cdkworkshop.com/20-typescript.html)
* [Video Introducing CDK by AWS with Demo](https://youtu.be/ZWCvNFUN-sU)
* [CDK Concepts](https://youtu.be/9As_ZIjUGmY)

## Related

Kong on AWS Hands on Workshop - https://kong.awsworkshop.io/
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

import aws_cdk.aws_autoscaling
import aws_cdk.aws_ec2
import aws_cdk.aws_eks
import aws_cdk.aws_rds
import aws_cdk.aws_sqs
import aws_cdk.core


class AutoScalar(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.AutoScalar",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        namespace: builtins.str,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param namespace: 
        :param nodegroup: 
        '''
        props = AutoScalarProps(
            cluster=cluster, namespace=namespace, nodegroup=nodegroup
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="kong-core.AutoScalarProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "namespace": "namespace",
        "nodegroup": "nodegroup",
    },
)
class AutoScalarProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        namespace: builtins.str,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
    ) -> None:
        '''
        :param cluster: 
        :param namespace: 
        :param nodegroup: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "namespace": namespace,
            "nodegroup": nodegroup,
        }

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nodegroup(self) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        result = self._values.get("nodegroup")
        assert result is not None, "Required property 'nodegroup' is missing"
        return typing.cast(aws_cdk.aws_autoscaling.AutoScalingGroup, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalarProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertManager(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.CertManager",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cacertname: builtins.str,
        cluster: aws_cdk.aws_eks.Cluster,
        cluster_issuer_name: builtins.str,
        dns_names: typing.Sequence[builtins.str],
        hosted_zone_name: builtins.str,
        namespace: builtins.str,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
        private_ca_arn: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cacertname: 
        :param cluster: 
        :param cluster_issuer_name: 
        :param dns_names: 
        :param hosted_zone_name: 
        :param namespace: 
        :param nodegroup: 
        :param private_ca_arn: 
        '''
        props = CertManagerProps(
            cacertname=cacertname,
            cluster=cluster,
            cluster_issuer_name=cluster_issuer_name,
            dns_names=dns_names,
            hosted_zone_name=hosted_zone_name,
            namespace=namespace,
            nodegroup=nodegroup,
            private_ca_arn=private_ca_arn,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="kong-core.CertManagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "cacertname": "cacertname",
        "cluster": "cluster",
        "cluster_issuer_name": "clusterIssuerName",
        "dns_names": "dnsNames",
        "hosted_zone_name": "hostedZoneName",
        "namespace": "namespace",
        "nodegroup": "nodegroup",
        "private_ca_arn": "privateCaArn",
    },
)
class CertManagerProps:
    def __init__(
        self,
        *,
        cacertname: builtins.str,
        cluster: aws_cdk.aws_eks.Cluster,
        cluster_issuer_name: builtins.str,
        dns_names: typing.Sequence[builtins.str],
        hosted_zone_name: builtins.str,
        namespace: builtins.str,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
        private_ca_arn: builtins.str,
    ) -> None:
        '''
        :param cacertname: 
        :param cluster: 
        :param cluster_issuer_name: 
        :param dns_names: 
        :param hosted_zone_name: 
        :param namespace: 
        :param nodegroup: 
        :param private_ca_arn: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cacertname": cacertname,
            "cluster": cluster,
            "cluster_issuer_name": cluster_issuer_name,
            "dns_names": dns_names,
            "hosted_zone_name": hosted_zone_name,
            "namespace": namespace,
            "nodegroup": nodegroup,
            "private_ca_arn": private_ca_arn,
        }

    @builtins.property
    def cacertname(self) -> builtins.str:
        result = self._values.get("cacertname")
        assert result is not None, "Required property 'cacertname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    @builtins.property
    def cluster_issuer_name(self) -> builtins.str:
        result = self._values.get("cluster_issuer_name")
        assert result is not None, "Required property 'cluster_issuer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dns_names(self) -> typing.List[builtins.str]:
        result = self._values.get("dns_names")
        assert result is not None, "Required property 'dns_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def hosted_zone_name(self) -> builtins.str:
        result = self._values.get("hosted_zone_name")
        assert result is not None, "Required property 'hosted_zone_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nodegroup(self) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        result = self._values.get("nodegroup")
        assert result is not None, "Required property 'nodegroup' is missing"
        return typing.cast(aws_cdk.aws_autoscaling.AutoScalingGroup, result)

    @builtins.property
    def private_ca_arn(self) -> builtins.str:
        result = self._values.get("private_ca_arn")
        assert result is not None, "Required property 'private_ca_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertManagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EksNodeHandler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.EksNodeHandler",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param nodegroup: 
        '''
        props = NodeHandlerProps(cluster=cluster, nodegroup=nodegroup)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationQueue")
    def notification_queue(self) -> aws_cdk.aws_sqs.Queue:
        return typing.cast(aws_cdk.aws_sqs.Queue, jsii.get(self, "notificationQueue"))

    @notification_queue.setter
    def notification_queue(self, value: aws_cdk.aws_sqs.Queue) -> None:
        jsii.set(self, "notificationQueue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> aws_cdk.aws_eks.ServiceAccount:
        return typing.cast(aws_cdk.aws_eks.ServiceAccount, jsii.get(self, "serviceAccount"))

    @service_account.setter
    def service_account(self, value: aws_cdk.aws_eks.ServiceAccount) -> None:
        jsii.set(self, "serviceAccount", value)


class ElastiCacheStack(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.ElastiCacheStack",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        numberofnodegroups: jsii.Number,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param numberofnodegroups: 
        :param vpc: 
        '''
        props = ElastiCacheStackProps(numberofnodegroups=numberofnodegroups, vpc=vpc)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="kong-core.ElastiCacheStackProps",
    jsii_struct_bases=[],
    name_mapping={"numberofnodegroups": "numberofnodegroups", "vpc": "vpc"},
)
class ElastiCacheStackProps:
    def __init__(
        self,
        *,
        numberofnodegroups: jsii.Number,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param numberofnodegroups: 
        :param vpc: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "numberofnodegroups": numberofnodegroups,
            "vpc": vpc,
        }

    @builtins.property
    def numberofnodegroups(self) -> jsii.Number:
        result = self._values.get("numberofnodegroups")
        assert result is not None, "Required property 'numberofnodegroups' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastiCacheStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="kong-core.KongEksControlPlaneProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_dns": "clusterDns",
        "control_plane_cluster_props": "controlPlaneClusterProps",
        "control_plane_node_props": "controlPlaneNodeProps",
        "namespace": "namespace",
        "rds_props": "rdsProps",
        "telemetry_dns": "telemetryDns",
    },
)
class KongEksControlPlaneProps:
    def __init__(
        self,
        *,
        cluster_dns: builtins.str,
        control_plane_cluster_props: aws_cdk.aws_eks.ClusterProps,
        control_plane_node_props: aws_cdk.aws_eks.AutoScalingGroupCapacityOptions,
        namespace: builtins.str,
        rds_props: "RdsDatabaseProps",
        telemetry_dns: builtins.str,
    ) -> None:
        '''
        :param cluster_dns: 
        :param control_plane_cluster_props: 
        :param control_plane_node_props: 
        :param namespace: 
        :param rds_props: 
        :param telemetry_dns: 
        '''
        if isinstance(control_plane_cluster_props, dict):
            control_plane_cluster_props = aws_cdk.aws_eks.ClusterProps(**control_plane_cluster_props)
        if isinstance(control_plane_node_props, dict):
            control_plane_node_props = aws_cdk.aws_eks.AutoScalingGroupCapacityOptions(**control_plane_node_props)
        if isinstance(rds_props, dict):
            rds_props = RdsDatabaseProps(**rds_props)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_dns": cluster_dns,
            "control_plane_cluster_props": control_plane_cluster_props,
            "control_plane_node_props": control_plane_node_props,
            "namespace": namespace,
            "rds_props": rds_props,
            "telemetry_dns": telemetry_dns,
        }

    @builtins.property
    def cluster_dns(self) -> builtins.str:
        result = self._values.get("cluster_dns")
        assert result is not None, "Required property 'cluster_dns' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def control_plane_cluster_props(self) -> aws_cdk.aws_eks.ClusterProps:
        '''
        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/
        :aws-cdk_aws-eks: .ClusterProps.html
        :summary: Control Plane EKS Cluster properties
        '''
        result = self._values.get("control_plane_cluster_props")
        assert result is not None, "Required property 'control_plane_cluster_props' is missing"
        return typing.cast(aws_cdk.aws_eks.ClusterProps, result)

    @builtins.property
    def control_plane_node_props(
        self,
    ) -> aws_cdk.aws_eks.AutoScalingGroupCapacityOptions:
        '''
        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/
        :aws-cdk_aws-eks: .AutoScalingGroupCapacityOptions.html
        :summary: Kong Control Plane EKS Nodes properties
        '''
        result = self._values.get("control_plane_node_props")
        assert result is not None, "Required property 'control_plane_node_props' is missing"
        return typing.cast(aws_cdk.aws_eks.AutoScalingGroupCapacityOptions, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rds_props(self) -> "RdsDatabaseProps":
        '''
        :summary: RDS Database properties
        '''
        result = self._values.get("rds_props")
        assert result is not None, "Required property 'rds_props' is missing"
        return typing.cast("RdsDatabaseProps", result)

    @builtins.property
    def telemetry_dns(self) -> builtins.str:
        result = self._values.get("telemetry_dns")
        assert result is not None, "Required property 'telemetry_dns' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KongEksControlPlaneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="kong-core.KongEksDataPlaneProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_dns": "clusterDns",
        "data_plane_cluster_props": "dataPlaneClusterProps",
        "data_plane_node_props": "dataPlaneNodeProps",
        "private_ca_arn": "privateCaArn",
        "telemetry_dns": "telemetryDns",
    },
)
class KongEksDataPlaneProps:
    def __init__(
        self,
        *,
        cluster_dns: builtins.str,
        data_plane_cluster_props: aws_cdk.aws_eks.ClusterProps,
        data_plane_node_props: aws_cdk.aws_eks.AutoScalingGroupCapacityOptions,
        private_ca_arn: builtins.str,
        telemetry_dns: builtins.str,
    ) -> None:
        '''
        :param cluster_dns: 
        :param data_plane_cluster_props: 
        :param data_plane_node_props: 
        :param private_ca_arn: 
        :param telemetry_dns: 
        '''
        if isinstance(data_plane_cluster_props, dict):
            data_plane_cluster_props = aws_cdk.aws_eks.ClusterProps(**data_plane_cluster_props)
        if isinstance(data_plane_node_props, dict):
            data_plane_node_props = aws_cdk.aws_eks.AutoScalingGroupCapacityOptions(**data_plane_node_props)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_dns": cluster_dns,
            "data_plane_cluster_props": data_plane_cluster_props,
            "data_plane_node_props": data_plane_node_props,
            "private_ca_arn": private_ca_arn,
            "telemetry_dns": telemetry_dns,
        }

    @builtins.property
    def cluster_dns(self) -> builtins.str:
        result = self._values.get("cluster_dns")
        assert result is not None, "Required property 'cluster_dns' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_plane_cluster_props(self) -> aws_cdk.aws_eks.ClusterProps:
        '''
        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/
        :aws-cdk_aws-eks: .ClusterProps.html
        :summary: Control Plane EKS Cluster properties
        '''
        result = self._values.get("data_plane_cluster_props")
        assert result is not None, "Required property 'data_plane_cluster_props' is missing"
        return typing.cast(aws_cdk.aws_eks.ClusterProps, result)

    @builtins.property
    def data_plane_node_props(self) -> aws_cdk.aws_eks.AutoScalingGroupCapacityOptions:
        '''
        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/
        :aws-cdk_aws-eks: .AutoScalingGroupCapacityOptions.html
        :summary: Kong Data Plane EKS Nodes properties
        '''
        result = self._values.get("data_plane_node_props")
        assert result is not None, "Required property 'data_plane_node_props' is missing"
        return typing.cast(aws_cdk.aws_eks.AutoScalingGroupCapacityOptions, result)

    @builtins.property
    def private_ca_arn(self) -> builtins.str:
        result = self._values.get("private_ca_arn")
        assert result is not None, "Required property 'private_ca_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def telemetry_dns(self) -> builtins.str:
        result = self._values.get("telemetry_dns")
        assert result is not None, "Required property 'telemetry_dns' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KongEksDataPlaneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetricsServer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.MetricsServer",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        '''
        props = MetricsServerProps(cluster=cluster)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="kong-core.MetricsServerProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster"},
)
class MetricsServerProps:
    def __init__(self, *, cluster: aws_cdk.aws_eks.Cluster) -> None:
        '''
        :param cluster: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
        }

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetricsServerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="kong-core.NodeHandlerProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster", "nodegroup": "nodegroup"},
)
class NodeHandlerProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
    ) -> None:
        '''
        :param cluster: 
        :param nodegroup: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "nodegroup": nodegroup,
        }

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    @builtins.property
    def nodegroup(self) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        result = self._values.get("nodegroup")
        assert result is not None, "Required property 'nodegroup' is missing"
        return typing.cast(aws_cdk.aws_autoscaling.AutoScalingGroup, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodeHandlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="kong-core.RdsDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "databasename": "databasename",
        "postgresversion": "postgresversion",
        "username": "username",
    },
)
class RdsDatabaseProps:
    def __init__(
        self,
        *,
        databasename: builtins.str,
        postgresversion: aws_cdk.aws_rds.PostgresEngineVersion,
        username: builtins.str,
    ) -> None:
        '''
        :param databasename: 
        :param postgresversion: 
        :param username: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "databasename": databasename,
            "postgresversion": postgresversion,
            "username": username,
        }

    @builtins.property
    def databasename(self) -> builtins.str:
        '''
        :summary: Database name to be used for Artifactory
        '''
        result = self._values.get("databasename")
        assert result is not None, "Required property 'databasename' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def postgresversion(self) -> aws_cdk.aws_rds.PostgresEngineVersion:
        '''
        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/
        :aws-cdk_aws-rds: .PostgresEngineVersion.html
        :summary: RDS PostGres Engine Version
        '''
        result = self._values.get("postgresversion")
        assert result is not None, "Required property 'postgresversion' is missing"
        return typing.cast(aws_cdk.aws_rds.PostgresEngineVersion, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :summary: Master username to be used for RDS
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="kong-core.RdsProps",
    jsii_struct_bases=[],
    name_mapping={
        "databasename": "databasename",
        "postgresversion": "postgresversion",
        "username": "username",
        "vpc": "vpc",
    },
)
class RdsProps:
    def __init__(
        self,
        *,
        databasename: builtins.str,
        postgresversion: aws_cdk.aws_rds.PostgresEngineVersion,
        username: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param databasename: 
        :param postgresversion: 
        :param username: 
        :param vpc: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "databasename": databasename,
            "postgresversion": postgresversion,
            "username": username,
            "vpc": vpc,
        }

    @builtins.property
    def databasename(self) -> builtins.str:
        result = self._values.get("databasename")
        assert result is not None, "Required property 'databasename' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def postgresversion(self) -> aws_cdk.aws_rds.PostgresEngineVersion:
        result = self._values.get("postgresversion")
        assert result is not None, "Required property 'postgresversion' is missing"
        return typing.cast(aws_cdk.aws_rds.PostgresEngineVersion, result)

    @builtins.property
    def username(self) -> builtins.str:
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsStack(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.RdsStack",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        databasename: builtins.str,
        postgresversion: aws_cdk.aws_rds.PostgresEngineVersion,
        username: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param databasename: 
        :param postgresversion: 
        :param username: 
        :param vpc: 
        '''
        props = RdsProps(
            databasename=databasename,
            postgresversion=postgresversion,
            username=username,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kongPostgresSql")
    def kong_postgres_sql(self) -> aws_cdk.aws_rds.DatabaseInstance:
        return typing.cast(aws_cdk.aws_rds.DatabaseInstance, jsii.get(self, "kongPostgresSql"))

    @kong_postgres_sql.setter
    def kong_postgres_sql(self, value: aws_cdk.aws_rds.DatabaseInstance) -> None:
        jsii.set(self, "kongPostgresSql", value)


class SecretsManager(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.SecretsManager",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        namespace: builtins.str,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param namespace: 
        :param nodegroup: 
        '''
        props = SecretsManagerProps(
            cluster=cluster, namespace=namespace, nodegroup=nodegroup
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="kong-core.SecretsManagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "namespace": "namespace",
        "nodegroup": "nodegroup",
    },
)
class SecretsManagerProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        namespace: builtins.str,
        nodegroup: aws_cdk.aws_autoscaling.AutoScalingGroup,
    ) -> None:
        '''
        :param cluster: 
        :param namespace: 
        :param nodegroup: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "namespace": namespace,
            "nodegroup": nodegroup,
        }

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nodegroup(self) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        result = self._values.get("nodegroup")
        assert result is not None, "Required property 'nodegroup' is missing"
        return typing.cast(aws_cdk.aws_autoscaling.AutoScalingGroup, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretsManagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Telemetry(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-core.Telemetry",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        namespace: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param namespace: 
        '''
        props = TelemetryProps(cluster=cluster, namespace=namespace)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="kong-core.TelemetryProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster", "namespace": "namespace"},
)
class TelemetryProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        namespace: builtins.str,
    ) -> None:
        '''
        :param cluster: 
        :param namespace: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "namespace": namespace,
        }

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TelemetryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AutoScalar",
    "AutoScalarProps",
    "CertManager",
    "CertManagerProps",
    "EksNodeHandler",
    "ElastiCacheStack",
    "ElastiCacheStackProps",
    "KongEksControlPlaneProps",
    "KongEksDataPlaneProps",
    "MetricsServer",
    "MetricsServerProps",
    "NodeHandlerProps",
    "RdsDatabaseProps",
    "RdsProps",
    "RdsStack",
    "SecretsManager",
    "SecretsManagerProps",
    "Telemetry",
    "TelemetryProps",
]

publication.publish()
