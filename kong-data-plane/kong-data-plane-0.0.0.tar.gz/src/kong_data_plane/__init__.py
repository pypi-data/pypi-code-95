'''
# kong-data-plane

[![NPM version](https://badge.fury.io/js/kong-data-plane.svg)](https://badge.fury.io/js/kong-data-plane)
[![PyPI version](https://badge.fury.io/py/kong-data-plane.svg)](https://badge.fury.io/py/kong-data-plane)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/kong-data-plane?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/kong-data-plane?label=pypi&color=blue)

Use this Kong CDK Construct Library to deploy Kong data plane on Amazon EKS .

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

## npm Package Installation:

```
yarn add --dev kong-data-plane
# or
npm install kong-data-plane --save-dev
```

## PyPI Package Installation:

```
pip install kong-data-plane
```

# Sample

Try out https://github.com/kong/aws-samples for the complete sample application and instructions.

## Resources to learn about CDK

* [CDK TypeScript Workshop](https://cdkworkshop.com/20-typescript.html)
* [Video Introducing CDK by AWS with Demo](https://youtu.be/ZWCvNFUN-sU)
* [CDK Concepts](https://youtu.be/9As_ZIjUGmY)

## Kong Hands on Workshop

https://kong.awsworkshop.io/
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
    jsii_type="kong-data-plane.KongEks",
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
        data_plane_cluster_props: aws_cdk.aws_eks.ClusterProps,
        data_plane_node_props: aws_cdk.aws_eks.AutoScalingGroupCapacityOptions,
        private_ca_arn: builtins.str,
        telemetry_dns: builtins.str,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cluster_dns: 
        :param data_plane_cluster_props: 
        :param data_plane_node_props: 
        :param private_ca_arn: 
        :param telemetry_dns: 

        :access: public
        :since: 0.1.0
        :summary: Constructs a new instance of the KongEks class.
        '''
        props = kong_core.KongEksDataPlaneProps(
            cluster_dns=cluster_dns,
            data_plane_cluster_props=data_plane_cluster_props,
            data_plane_node_props=data_plane_node_props,
            private_ca_arn=private_ca_arn,
            telemetry_dns=telemetry_dns,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "KongEks",
]

publication.publish()
