'''
# kong-control-plane

[![NPM version](https://badge.fury.io/js/kong-control-plane.svg)](https://badge.fury.io/js/kong-control-plane)
[![PyPI version](https://badge.fury.io/py/kong-control-plane.svg)](https://badge.fury.io/py/kong-control-plane)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/kong-control-plane?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/kong-control-plane?label=pypi&color=blue)

Use this Kong CDK Construct Library to deploy Kong control plane on Amazon EKS .

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
yarn add --dev kong-control-plane
# or
npm install kong-control-plane --save-dev
```

## PyPI Package Installation:

```
pip install kong-control-plane
```

# Sample

Try out https://github.com/kong/aws-samples for the complete sample application and instructions.

## Resources to learn about CDK

* [CDK TypeScript Workshop](https://cdkworkshop.com/20-typescript.html)
* [Video Introducing CDK by AWS with Demo](https://youtu.be/ZWCvNFUN-sU)
* [CDK Concepts](https://youtu.be/9As_ZIjUGmY)

## Related

Kong on AWS Hands on Workshop - https://kong.awsworkshop.io/
Kong Data plane on AWS contruct - FILLME
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

import aws_cdk.aws_eks
import aws_cdk.core
import kong_core


class KongEks(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="kong-control-plane.KongEks",
):
    '''
    :summary: The KongEks class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster_dns: builtins.str,
        control_plane_cluster_props: aws_cdk.aws_eks.ClusterProps,
        control_plane_node_props: aws_cdk.aws_eks.AutoScalingGroupCapacityOptions,
        namespace: builtins.str,
        rds_props: kong_core.RdsDatabaseProps,
        telemetry_dns: builtins.str,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cluster_dns: 
        :param control_plane_cluster_props: 
        :param control_plane_node_props: 
        :param namespace: 
        :param rds_props: 
        :param telemetry_dns: 

        :access: public
        :since: 0.1.0
        :summary: Constructs a new instance of the KongEks class.
        '''
        props = kong_core.KongEksControlPlaneProps(
            cluster_dns=cluster_dns,
            control_plane_cluster_props=control_plane_cluster_props,
            control_plane_node_props=control_plane_node_props,
            namespace=namespace,
            rds_props=rds_props,
            telemetry_dns=telemetry_dns,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlPlane")
    def control_plane(self) -> aws_cdk.aws_eks.Cluster:
        return typing.cast(aws_cdk.aws_eks.Cluster, jsii.get(self, "controlPlane"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateCaArn")
    def private_ca_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateCaArn"))

    @private_ca_arn.setter
    def private_ca_arn(self, value: builtins.str) -> None:
        jsii.set(self, "privateCaArn", value)


__all__ = [
    "KongEks",
]

publication.publish()
