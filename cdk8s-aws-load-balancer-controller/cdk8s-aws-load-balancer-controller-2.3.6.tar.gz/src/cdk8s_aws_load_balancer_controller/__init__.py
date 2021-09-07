'''
[![NPM version](https://badge.fury.io/js/cdk8s-aws-load-balancer-controller.svg)](https://badge.fury.io/js/cdk8s-aws-load-balancer-controller)
[![PyPI version](https://badge.fury.io/py/cdk8s-aws-load-balancer-controller.svg)](https://badge.fury.io/py/cdk8s-aws-load-balancer-controller)
![Release](https://github.com/neilkuan/cdk8s-aws-load-balancer-controller/workflows/Release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk8s-aws-load-balancer-controller?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk8s-aws-load-balancer-controller?label=pypi&color=blue)

# cdk8s-aws-load-balancer-controller

> [cdk8s aws load balancer controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller) constructs for cdk8s

This project was formerly known as "CDK AWS ALB Ingress Controller", I just rename it to be "CDK AWS Load Balancer Controller".

Basic implementation of a [aws load balancer controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller) construct for cdk8s. Contributions are welcome!

## Before Usage need to install helm

```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

## Usage

```bash
npm i cdk8s-aws-load-balancer-controller
npm i cdk8s
or
yarn add cdk8s-aws-load-balancer-controller
yarn add cdk8s
```

### AWS Load Balance Controller V1

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk8s import App, Chart
from constructs import Construct
from cdk8s_aws_load_balancer_controller import AlbIngressController

class MyChart(Chart):
    def __init__(self, scope, name):
        super().__init__(scope, name)
        AlbIngressController(self, "albingresscntroller",
            cluster_name="EKScluster"
        )
app = App()
MyChart(app, "testcdk8s")
app.synth()
```

### AWS Load Balance Controller V2

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk8s import App, Chart
from cdk8s_aws_load_balancer_controller import AwsLoadBalancerController
import constructs as constructs

class MyChart(Chart):
    def __init__(self, scope, name, *, clusterName):
        super().__init__(scope, name)
        alb = AwsLoadBalancerController(self, "alb",
            cluster_name=cluster_name,
            create_service_account=False
        )
        self.deployment_name = alb.deployment_name
        self.deployment_name_space = alb.namespace
app = App()
MyChart(app, "testcdk8s")
app.synth()
```

### AWS Load Balance Controller V2 specific Namespace.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk8s import App, Chart
from cdk8s_aws_load_balancer_controller import AwsLoadBalancerController
import constructs as constructs

class MyChart(Chart):
    def __init__(self, scope, name, *, clusterName):
        super().__init__(scope, name)
        alb = AwsLoadBalancerController(self, "alb",
            cluster_name=cluster_name,
            create_service_account=False,
            namespace="kube-system"
        )
        self.deployment_name = alb.deployment_name
        self.deployment_name_space = alb.namespace
app = App()
MyChart(app, "testcdk8s")
app.synth()
```

# Featrue For Add IAM Policy.

* For IRSA add IAM Policy version 1.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# CDK APP like eks_cluster.ts
from cdk8s_aws_load_balancer_controller import AwsLoadBalancePolicy, VersionsLists
import aws_cdk.aws_eks as eks
cluster = eks.Cluster(self, "MyK8SCluster",
    default_capacity=0,
    masters_role=cluster_admin,
    version=eks.KubernetesVersion.V1_18
)

alb_service_account = cluster.add_service_account("alb-ingress-controller",
    name="alb-ingress-controller",
    namespace="kube-system"
)
# will help you add policy to IAM Role .
AwsLoadBalancePolicy.add_policy(VersionsLists.AWS_LOAD_BALANCER_CONTROLLER_POLICY_V1, alb_service_account)
```

* For IRSA add IAM Policy version 2.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# CDK APP like eks_cluster.ts
from cdk8s_aws_load_balancer_controller import AwsLoadBalancePolicy, VersionsLists
import aws_cdk.aws_eks as eks
cluster = eks.Cluster(self, "MyK8SCluster",
    default_capacity=0,
    masters_role=cluster_admin,
    version=eks.KubernetesVersion.V1_18
)

sa = eks.ServiceAccount(self, "albserviceaccount",
    cluster=cluster,
    name="aws-load-balancer-controller"
)
AwsLoadBalancePolicy.add_policy(VersionsLists.AWS_LOAD_BALANCER_CONTROLLER_POLICY_V2, sa)
```

Also can see [example repo 1](https://github.com/neilkuan/cdk8s-cdk-example)
or [example repo 2](https://github.com/neilkuan/eks-mgng-tagging-name.git) work with aws cdk.

## License

Distributed under the [Apache 2.0](./LICENSE) license.
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


class AlbIngressController(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-aws-load-balancer-controller.AlbIngressController",
):
    '''Generate alb-ingress-controller config yaml.

    see https://github.com/kubernetes-sigs/aws-alb-ingress-controller/blob/master/docs/examples
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        env: typing.Optional[typing.Sequence["EnvVar"]] = None,
        image: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        replicas: typing.Optional[jsii.Number] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_name: Kubernetes Cluster Name for alb-ingress-controller. Default: - None
        :param args: Another Args for alb-ingress-controller. Default: - None
        :param env: Another Args for alb-ingress-controller. Default: - None
        :param image: Default image for alb-ingress-controller. Default: - docker.io/amazon/aws-alb-ingress-controller:v1.1.9
        :param labels: Extra labels to associate with resources. Default: - none
        :param namespace: Default Namespace for alb-ingress-controller. Default: - kube-system
        :param replicas: Replicas for alb-ingress-controller. Default: - 1
        :param service_account_name: Default Service Account Name for alb-ingress-controller. Default: - alb-ingress-controller
        '''
        options = AlbIngressControllerOptions(
            cluster_name=cluster_name,
            args=args,
            env=env,
            image=image,
            labels=labels,
            namespace=namespace,
            replicas=replicas,
            service_account_name=service_account_name,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''Kubernetes Cluster Name for alb-ingress-controller.'''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentName")
    def deployment_name(self) -> builtins.str:
        '''Kubernetes Deployment Name for alb-ingress-controller.'''
        return typing.cast(builtins.str, jsii.get(self, "deploymentName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        '''Namespace for alb-ingress-controller.

        :default: - kube-system
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> builtins.str:
        '''Service Account Name for alb-ingress-controller.'''
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountName"))


@jsii.data_type(
    jsii_type="cdk8s-aws-load-balancer-controller.AlbIngressControllerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "args": "args",
        "env": "env",
        "image": "image",
        "labels": "labels",
        "namespace": "namespace",
        "replicas": "replicas",
        "service_account_name": "serviceAccountName",
    },
)
class AlbIngressControllerOptions:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        env: typing.Optional[typing.Sequence["EnvVar"]] = None,
        image: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        replicas: typing.Optional[jsii.Number] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cluster_name: Kubernetes Cluster Name for alb-ingress-controller. Default: - None
        :param args: Another Args for alb-ingress-controller. Default: - None
        :param env: Another Args for alb-ingress-controller. Default: - None
        :param image: Default image for alb-ingress-controller. Default: - docker.io/amazon/aws-alb-ingress-controller:v1.1.9
        :param labels: Extra labels to associate with resources. Default: - none
        :param namespace: Default Namespace for alb-ingress-controller. Default: - kube-system
        :param replicas: Replicas for alb-ingress-controller. Default: - 1
        :param service_account_name: Default Service Account Name for alb-ingress-controller. Default: - alb-ingress-controller
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
        }
        if args is not None:
            self._values["args"] = args
        if env is not None:
            self._values["env"] = env
        if image is not None:
            self._values["image"] = image
        if labels is not None:
            self._values["labels"] = labels
        if namespace is not None:
            self._values["namespace"] = namespace
        if replicas is not None:
            self._values["replicas"] = replicas
        if service_account_name is not None:
            self._values["service_account_name"] = service_account_name

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''Kubernetes Cluster Name for alb-ingress-controller.

        :default: - None
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Another Args for alb-ingress-controller.

        :default: - None
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.List["EnvVar"]]:
        '''Another Args for alb-ingress-controller.

        :default: - None
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.List["EnvVar"]], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''Default image for alb-ingress-controller.

        :default: - docker.io/amazon/aws-alb-ingress-controller:v1.1.9
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Extra labels to associate with resources.

        :default: - none
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Default Namespace for alb-ingress-controller.

        :default: - kube-system
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''Replicas for alb-ingress-controller.

        :default: - 1
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_account_name(self) -> typing.Optional[builtins.str]:
        '''Default Service Account Name for alb-ingress-controller.

        :default: - alb-ingress-controller
        '''
        result = self._values.get("service_account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbIngressControllerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsLoadBalancePolicy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-aws-load-balancer-controller.AwsLoadBalancePolicy",
):
    '''awsLoadBalancePolicy class ,help you add policy to your Iam Role for service account.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="addPolicy") # type: ignore[misc]
    @builtins.classmethod
    def add_policy(cls, version: builtins.str, role: typing.Any) -> None:
        '''
        :param version: -
        :param role: -
        '''
        return typing.cast(None, jsii.sinvoke(cls, "addPolicy", [version, role]))


class AwsLoadBalancerController(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-aws-load-balancer-controller.AwsLoadBalancerController",
):
    '''Generate aws-load-balancer-controller config yaml.

    see https://github.com/kubernetes-sigs/aws-aws-load-balancer-controller/blob/master/docs/install/v2_0_0_full.yaml
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        chart_version: typing.Optional[builtins.str] = None,
        create_service_account: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_name: Kubernetes Cluster Name for aws-load-balancer-controller. Default: - None
        :param chart_version: Helm Chart Version for aws-load-balancer-controller. Default: - latest Helm Chart version.
        :param create_service_account: service account for aws-load-balancer-controller. Default: - true
        :param namespace: Namespace for aws-load-balancer-controller. Default: - default
        '''
        options = AwsLoadBalancerControllerOptions(
            cluster_name=cluster_name,
            chart_version=chart_version,
            create_service_account=create_service_account,
            namespace=namespace,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="chartVersion")
    def chart_version(self) -> builtins.str:
        '''Helm Chart Version for aws-load-balancer-controller.

        :default: - latest Helm Chart version.
        '''
        return typing.cast(builtins.str, jsii.get(self, "chartVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''Kubernetes Cluster Name for aws-load-balancer-controller.'''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentName")
    def deployment_name(self) -> builtins.str:
        '''Kubernetes Deployment Name for aws-load-balancer-controller.'''
        return typing.cast(builtins.str, jsii.get(self, "deploymentName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        '''Namespace for aws-load-balancer-controller.

        :default: - default
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> builtins.str:
        '''Service Account Name for aws-load-balancer-controller.'''
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountName"))


@jsii.data_type(
    jsii_type="cdk8s-aws-load-balancer-controller.AwsLoadBalancerControllerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "chart_version": "chartVersion",
        "create_service_account": "createServiceAccount",
        "namespace": "namespace",
    },
)
class AwsLoadBalancerControllerOptions:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        chart_version: typing.Optional[builtins.str] = None,
        create_service_account: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cluster_name: Kubernetes Cluster Name for aws-load-balancer-controller. Default: - None
        :param chart_version: Helm Chart Version for aws-load-balancer-controller. Default: - latest Helm Chart version.
        :param create_service_account: service account for aws-load-balancer-controller. Default: - true
        :param namespace: Namespace for aws-load-balancer-controller. Default: - default
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
        }
        if chart_version is not None:
            self._values["chart_version"] = chart_version
        if create_service_account is not None:
            self._values["create_service_account"] = create_service_account
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''Kubernetes Cluster Name for aws-load-balancer-controller.

        :default: - None
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def chart_version(self) -> typing.Optional[builtins.str]:
        '''Helm Chart Version for aws-load-balancer-controller.

        :default: - latest Helm Chart version.
        '''
        result = self._values.get("chart_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_service_account(self) -> typing.Optional[builtins.bool]:
        '''service account for aws-load-balancer-controller.

        :default: - true
        '''
        result = self._values.get("create_service_account")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace for aws-load-balancer-controller.

        :default: - default
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsLoadBalancerControllerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertManager(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-aws-load-balancer-controller.CertManager",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="certManagerConfig") # type: ignore[misc]
    @builtins.classmethod
    def cert_manager_config(cls) -> typing.Any:
        return typing.cast(typing.Any, jsii.sinvoke(cls, "certManagerConfig", []))


@jsii.data_type(
    jsii_type="cdk8s-aws-load-balancer-controller.EnvVar",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class EnvVar:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Name of the environment variable. Must be a C_IDENTIFIER.
        :param value: Variable references $(VAR_NAME) are expanded using the previous defined environment variables in the container and any service environment variables. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Defaults to "". Default: .
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the environment variable.

        Must be a C_IDENTIFIER.

        :schema: io.k8s.api.core.v1.EnvVar#name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Variable references $(VAR_NAME) are expanded using the previous defined environment variables in the container and any service environment variables.

        If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Defaults to "".

        :default: .

        :schema: io.k8s.api.core.v1.EnvVar#value
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvVar(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-aws-load-balancer-controller.VersionsLists")
class VersionsLists(enum.Enum):
    AWS_LOAD_BALANCER_CONTROLLER_POLICY_V1 = "AWS_LOAD_BALANCER_CONTROLLER_POLICY_V1"
    AWS_LOAD_BALANCER_CONTROLLER_POLICY_V2 = "AWS_LOAD_BALANCER_CONTROLLER_POLICY_V2"


__all__ = [
    "AlbIngressController",
    "AlbIngressControllerOptions",
    "AwsLoadBalancePolicy",
    "AwsLoadBalancerController",
    "AwsLoadBalancerControllerOptions",
    "CertManager",
    "EnvVar",
    "VersionsLists",
]

publication.publish()
