'''
[![NPM version](https://badge.fury.io/js/cdk-k3s-cluster.svg)](https://badge.fury.io/js/cdk-k3s-cluster)
[![PyPI version](https://badge.fury.io/py/cdk-k3s-cluster.svg)](https://badge.fury.io/py/cdk-k3s-cluster)
![Release](https://github.com/aws-samples/aws-cdk-for-k3scluster/workflows/Release/badge.svg)

## What is cdk-k3s-cluster?

`cdk-k3s-cluster` is a new JSII construct library for AWS CDK that deploys a scalable Kubernetes [K3s](https://k3s.io/) cluster on **Graviton2 Arm-based** (mg6 by default) **Spot** instances with one ~~click~~ command on AWS.

## What problem does cdk-k3s-cluster solve?

`cdk-k3s-cluster` is just another way to deploy Kubernetes (`K3s` specifically) on AWS. `K3s` is a minimalist Kubernetes distribution from Rancher often related to Edge and IoT use cases. There is a gazillion of articles on the Internet about how to setup `K3s` on a Raspberry cluster. The great [Alex Ellis](https://twitter.com/alexellisuk) has a [blog post](https://blog.alexellis.io/test-drive-k3s-on-raspberry-pi/) on it, for example. Since I don't have a Raspberry cluster and I was not planning to buy one I thought I'd use the power of the cloud to mimic it. The result of this experiment is that you could deploy an ephemeral, cheap Kubernetes Arm-based cluster on AWS in a matter of minutes. Unleash your imagination re how you can use it (e.g. an ephemeral cluster part of your deployment pipeline in the cloud?). Note the class today only supports Arm-based instances for deomstration purposes but can easily be adapted to support x86-based instances.

## How do you deploy and consume cdk-k3s-cluster?

### The cdk-k3s-cluster Cluster API

The `Cluster` API available in the `cdk-k3s-cluster` library, not to be confused with the Kubernetes Cluster API project, allows you to build the k3s cluster on AWS with AWS CDK. This library is currently available in both `NPM` and `PyPi`.

Creating a default cluster could be as simple as:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import cdk_k3s_cluster as k3s

k3s.Cluster(stack, "Cluster")
```

See below for a complete example.

### Deployment

`cdk-k3s-cluster` first deploys a Graviton2 EC2 instance (`m6g.large` by default) where it starts the `K3s` control plane. The `kubeconfig` file generated and the `K3s` token are copied to an S3 bucket. It then creates an ASG that spins up the number of Graviton2 worker nodes that you specify (3 by default - the ceiling limit is based on your account limits). These instances launch `K3s` worker nodes that join the cluster by downloading the token from S3. Ultimately the CDK outputs the link to the `kubeconfig` file on your private S3 bucket for you to copy it and use it with `kubectl`. This construct can deploy the worker node instances using either the `on-demand` or the `Spot` life cycles to reduce costs further (`Spot` is used by default). This construct cretes by default a new VPC but it can be configured to deploy either on the `default` VPC in your account or on a specific existing VPC id.

This is a high level view of the architecture and the deployment flow described above:
![ks3clusterdeploy](./images/ks3clusterdeploy.png)

This is a screenshot of the cluster creation user experience using CDK:

![ks3clustercreatecluster](./images/ks3clustercreatecluster.png)

### Consumption

Once the `cdk-k3s-cluster` has been deployed, this a high level view of the consumption flow:
![ks3clusterconsume](./images/ks3clusterconsume.png)

This is an example of the cluster consumption user experience using the `aws cli` (used to copy the `kubeconfig` file from S3) and `kubectl`:

```bash
$ aws s3 cp s3://k3sCluster-clusterk3sbucketxxxxxxxxxxxxx/kubeconfig.yaml .
download: s3://k3sCluster-clusterk3sbucketxxxxxxxxxxxxx/kubeconfig.yaml to ./kubeconfig.yaml

$ kubectl get nodes --kubeconfig=./kubeconfig.yaml
NAME                                          STATUS   ROLES    AGE     VERSION
ip-172-31-43-198.us-west-2.compute.internal   Ready    master   2m49s   v1.16.9+k3s1
ip-172-31-10-252.us-west-2.compute.internal   Ready    <none>   15s     v1.16.13+k3s1
ip-172-31-18-126.us-west-2.compute.internal   Ready    <none>   8s      v1.16.13+k3s1
ip-172-31-60-174.us-west-2.compute.internal   Ready    <none>   1s      v1.16.13+k3s1
```

### How does this relate to EKS

It doesn't. As noted above, `cdk-k3s-cluster` is just yet another experimental and peculiar way to run Kubernetes on AWS.

## What are the running costs for a cluster built with cdk-k3s-cluster?

It obviously depends how many worker nodes you deploy. If we stick to all the defaults (`Spot` lifecycle and the `m6g.medium` instance type with 1 Graviton2 CPU and 4GB of memory), as of August 2020 the unit cost in `Oregon` is $0.0177 which translates to a unit cost of $0.1416 per 8 hours (a work day). A 3 worker nodes cluster would be $0.5664 (including the control plane) per 8 hours (or $1.6992 per 24 hours full day).

A *100 worker nodes cluster* (or 101 vCPUs and 404GB of memory) would be *$0.0177 x 101 = $1.7877 per hour* or $0.0177 x 101 x 24 = *$42.9048 per day*.

This does not include, for example, the costs of the S3 bucket (probably marginal) or network traffic.

## Getting started

`cdk-k3s-cluster` is available in both `NPM` and `PyPi` modules ready to be imported into your CDK program.

### I am a Typescript type of person

This is an example of how to consume the `NPM` module with a CDK application written in Typescript. If you need to setup your Typescript environment [this is a good guide](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-typescript.html).

```bash
$ mkdir myk3scluster-typescript
$ cd myk3scluster-typescript
# initialize the AWS CDK project
$ cdk init -l typescript
# install the cdk-k3s-cluster npm module
$ yarn add cdk-k3s-cluster
```

Update your `./bin/myk3scluster-typescript.ts` file with the following content.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
import aws_cdk.aws_ec2 as ec2
import cdk_k3s_cluster as k3s

app = cdk.App()

env = {
    "region": app.node.try_get_context("region") || process.env.CDK_INTEG_REGION || process.env.CDK_DEFAULT_REGION,
    "account": app.node.try_get_context("account") || process.env.CDK_INTEG_ACCOUNT || process.env.CDK_DEFAULT_ACCOUNT
}

stack = cdk.Stack(app, "k8sCluster", env=env)

k3s.Cluster(stack, "Cluster",
    vpc=k3s.VpcProvider.get_or_create(stack),
    spot_worker_nodes=True,
    worker_min_capacity=3,
    worker_instance_type=ec2.InstanceType("m6g.medium"),
    control_plane_instance_type=ec2.InstanceType("m6g.medium"),
    bucket_removal_policy=cdk.RemovalPolicy.DESTROY
)
```

In this `typescript` example, we are using all of the properties available today. Note that we set the bucket removal policy to `DESTROY` (this will remove completely the S3 bucket - the safe default behavior is to leave the bucket in the account). For an up to date list of all the properties please refer to the `API.md` file in this repo.

### I am a Python type of person

This is an example of how to consume the `PyPi` module with a CDK application written in Typescript. If you need to setup your Python environment [this is a good guide](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html).

```bash
$ mkdir myk3scluster-python
$ cd myk3scluster-python
# initialize the AWS CDK project
$ cdk init -l python
# activate the Python virtual environment
$ source .env/bin/activate
# install the dependencies
$ pip install cdk-k3s-cluster
```

Update your `./app.py` file with the following content. Note how, in this example, we are only using two of the parameters available. To use all the defaults you could use `cluster = k3s.Cluster(self, "MyK3sClusters")`:

```python
#!/usr/bin/env python3

from aws_cdk import core
import cdk_k3s_cluster as k3s

class K3sCluster(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        k3s.Cluster(self, "MyK3sClusters", worker_min_capacity=5, spot_worker_nodes=True)

app = core.App()
K3sCluster(app, "K3sCluster")
app.synth()
```

### Deploying the stack (regardless of the language you have used)

deploy the CDK stack:

```bash
# see the difference before the deployment
$ cdk diff
# deploy it
$ cdk deploy
```

If you want to deploy in an existing VPC use either `cdk deploy --context use_default_vpc=1` or `cdk deploy --context use_vpc_id=<vpc id>`

### Clean up

Cleaning up the environment is as easy as running `cdk destroy` from where you left your prompt.

## Known issues and limitations

* First and foremost this is a learning experiment. We have done limited tests with it.
* We have not tested this beyond a mere `kubectl get nodes` test. Let alone trying anything like [arkade](https://github.com/alexellis/arkade)
* `cdk-k3s-cluster` only deploys Arm-based instances. It would be trivial to add x86 based instances support but it's not there today
* All the control plane and worker nodes are deployed in public subnets and the SGs are fairly permissive in terms of "source". Picking private subnets would have probably broken the use case of deploying into the `default` VPC (which is handy). This prototype over-indexes more on deployment convenience and ease of use than on best practices. Be mindful of that
* The control plane instance always deploys `on-demand` while for worker nodes you can pick between `on-demand` and `Spot`
* The ASG for worker nodes is configured with a single parameter that becomes the `min`, `max` and `desired` count for the ASG
* For simplicity, both the control plane instance and the worker nodes share the same instance type

## Credits

This library has been authored by [Massimo](https://github.com/mreferre/) and [Pahud](https://github.com/pahud/).
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
import aws_cdk.core


class AmiProvider(metaclass=jsii.JSIIMeta, jsii_type="cdk-k3s-cluster.AmiProvider"):
    '''The AMI provider to get the latest Amazon Linux 2 AMI for ARM64.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiId")
    def ami_id(self) -> aws_cdk.aws_ec2.IMachineImage:
        return typing.cast(aws_cdk.aws_ec2.IMachineImage, jsii.get(self, "amiId"))


class Cluster(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-k3s-cluster.Cluster",
):
    '''Represents the k3sCluster construct.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        control_plane_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        spot_worker_nodes: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        worker_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        worker_min_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_removal_policy: The bucket removal policy. When specicified as ``DESTROY``, the S3 bucket for the cluster state will be completely removed on stack destroy. Default: - cdk.RemovalPolicy.RETAIN
        :param control_plane_instance_type: control plane node ec2 instance type. Default: mg6.medium
        :param spot_worker_nodes: Run worker nodes as EC2 Spot. Default: true
        :param vpc: VPC. Default: - create new VPC
        :param worker_instance_type: worker node instance type. Default: mg6.medium
        :param worker_min_capacity: minimal number of worker nodes. Default: 3
        '''
        props = ClusterProps(
            bucket_removal_policy=bucket_removal_policy,
            control_plane_instance_type=control_plane_instance_type,
            spot_worker_nodes=spot_worker_nodes,
            vpc=vpc,
            worker_instance_type=worker_instance_type,
            worker_min_capacity=worker_min_capacity,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlPlaneInstanceType")
    def control_plane_instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        '''The instance type of the control plane.'''
        return typing.cast(aws_cdk.aws_ec2.InstanceType, jsii.get(self, "controlPlaneInstanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUri")
    def endpoint_uri(self) -> builtins.str:
        '''The endpoint URL of the control plan.'''
        return typing.cast(builtins.str, jsii.get(self, "endpointUri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerInstanceType")
    def worker_instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        '''The instance type of the worker node.'''
        return typing.cast(aws_cdk.aws_ec2.InstanceType, jsii.get(self, "workerInstanceType"))


@jsii.data_type(
    jsii_type="cdk-k3s-cluster.ClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_removal_policy": "bucketRemovalPolicy",
        "control_plane_instance_type": "controlPlaneInstanceType",
        "spot_worker_nodes": "spotWorkerNodes",
        "vpc": "vpc",
        "worker_instance_type": "workerInstanceType",
        "worker_min_capacity": "workerMinCapacity",
    },
)
class ClusterProps:
    def __init__(
        self,
        *,
        bucket_removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        control_plane_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        spot_worker_nodes: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        worker_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        worker_min_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param bucket_removal_policy: The bucket removal policy. When specicified as ``DESTROY``, the S3 bucket for the cluster state will be completely removed on stack destroy. Default: - cdk.RemovalPolicy.RETAIN
        :param control_plane_instance_type: control plane node ec2 instance type. Default: mg6.medium
        :param spot_worker_nodes: Run worker nodes as EC2 Spot. Default: true
        :param vpc: VPC. Default: - create new VPC
        :param worker_instance_type: worker node instance type. Default: mg6.medium
        :param worker_min_capacity: minimal number of worker nodes. Default: 3
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_removal_policy is not None:
            self._values["bucket_removal_policy"] = bucket_removal_policy
        if control_plane_instance_type is not None:
            self._values["control_plane_instance_type"] = control_plane_instance_type
        if spot_worker_nodes is not None:
            self._values["spot_worker_nodes"] = spot_worker_nodes
        if vpc is not None:
            self._values["vpc"] = vpc
        if worker_instance_type is not None:
            self._values["worker_instance_type"] = worker_instance_type
        if worker_min_capacity is not None:
            self._values["worker_min_capacity"] = worker_min_capacity

    @builtins.property
    def bucket_removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''The bucket removal policy.

        When specicified as ``DESTROY``, the S3 bucket for the cluster state
        will be completely removed on stack destroy.

        :default: - cdk.RemovalPolicy.RETAIN
        '''
        result = self._values.get("bucket_removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def control_plane_instance_type(
        self,
    ) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''control plane node ec2 instance type.

        :default: mg6.medium
        '''
        result = self._values.get("control_plane_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def spot_worker_nodes(self) -> typing.Optional[builtins.bool]:
        '''Run worker nodes as EC2 Spot.

        :default: true
        '''
        result = self._values.get("spot_worker_nodes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC.

        :default: - create new VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def worker_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''worker node instance type.

        :default: mg6.medium
        '''
        result = self._values.get("worker_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def worker_min_capacity(self) -> typing.Optional[jsii.Number]:
        '''minimal number of worker nodes.

        :default: 3
        '''
        result = self._values.get("worker_min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpcProvider(metaclass=jsii.JSIIMeta, jsii_type="cdk-k3s-cluster.VpcProvider"):
    '''The VPC provider to create or import the VPC.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(cls, scope: aws_cdk.core.Construct) -> aws_cdk.aws_ec2.IVpc:
        '''
        :param scope: -
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.sinvoke(cls, "getOrCreate", [scope]))


__all__ = [
    "AmiProvider",
    "Cluster",
    "ClusterProps",
    "VpcProvider",
]

publication.publish()
