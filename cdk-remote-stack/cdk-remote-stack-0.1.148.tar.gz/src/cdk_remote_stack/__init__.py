'''
[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/cdk-remote-stack.svg)](https://badge.fury.io/js/cdk-remote-stack)
[![PyPI version](https://badge.fury.io/py/cdk-remote-stack.svg)](https://badge.fury.io/py/cdk-remote-stack)
[![Build](https://github.com/pahud/cdk-remote-stack/actions/workflows/build.yml/badge.svg)](https://github.com/pahud/cdk-remote-stack/actions/workflows/build.yml)

# cdk-remote-stack

Get outputs from cross-regional AWS CDK stacks

# Why

AWS CDK cross-regional cross-stack reference is not easy with the native AWS CDK construct library.

`cdk-remote-stack` aims to simplify the cross-regional cross-stack reference to help you easily build cross-regional multi-stack AWS CDK apps.

This construct library provides two major constructs:

* **RemoteOutputs** - cross regional stack outputs reference.
* **RemoteParameters** - cross regional/account SSM parameters reference.

# RemoteOutputs

`RemoteOutputs` is ideal for one stack referencing the outputs from another across different AWS regions.

Let's say we have two cross-regional CDK stacks in the same cdk app:

1. **stackJP** - cdk stack in `JP` to create a SNS topic
2. **stackUS** - cdk stack in `US` to get the Outputs from `stackJP` and print out the SNS `TopicName` from `stackJP` Outputs.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_remote_stack import RemoteOutputs
import aws_cdk.core as cdk

app = cdk.App()

env_jP = {
    "region": "ap-northeast-1",
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

env_uS = {
    "region": "us-west-2",
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

# first stack in JP
stack_jP = cdk.Stack(app, "demo-stack-jp", env=env_jP)

cdk.CfnOutput(stack_jP, "TopicName", value="foo")

# second stack in US
stack_uS = cdk.Stack(app, "demo-stack-us", env=env_uS)

# ensure the dependency
stack_uS.add_dependency(stack_jP)

# get the stackJP stack outputs from stackUS
outputs = RemoteOutputs(stack_uS, "Outputs", stack=stack_jP)

remote_output_value = outputs.get("TopicName")

# the value should be exactly the same with the output value of `TopicName`
cdk.CfnOutput(stack_uS, "RemoteTopicName", value=remote_output_value)
```

At this moment, `RemoteOutputs` only supports cross-regional reference in a single AWS account.

## always get the latest stack output

By default, the `RemoteOutputs` construct will always try to get the latest output from the source stack. You may opt out by setting `alwaysUpdate` to `false` to turn this feature off.

For example:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
outputs = RemoteOutputs(stack_uS, "Outputs",
    stack=stack_jP,
    always_update=False
)
```

# RemoteParameters

AWS [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) is great to store and persist parameters and allow stacks from other regons/accounts to reference. Let's dive into the two major scenarios below:

## #1 - Stacks from single account and different regions

In this sample, we create two stacks from JP(`ap-northeast-1`) and US(`us-west-2`). The JP stack will produce and update parameters in its parameter store, while the US stack will consume the parameters across differnt regions with the `RemoteParameters` construct.

![](images/remote-param-1.svg)

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
env_jP = {"region": "ap-northeast-1", "account": "111111111111"}
env_uS = {"region": "us-west-2", "account": "111111111111"}

# first stack in JP
producer_stack_name = "demo-stack-jp"
stack_jP = cdk.Stack(app, producer_stack_name, env=env_jP)
parameter_path = f"/{envJP.account}/{envJP.region}/{producerStackName}"

ssm.StringParameter(stack_jP, "foo1",
    parameter_name=f"{parameterPath}/foo1",
    string_value="bar1"
)
ssm.StringParameter(stack_jP, "foo2",
    parameter_name=f"{parameterPath}/foo2",
    string_value="bar2"
)
ssm.StringParameter(stack_jP, "foo3",
    parameter_name=f"{parameterPath}/foo3",
    string_value="bar3"
)

# second stack in US
stack_uS = cdk.Stack(app, "demo-stack-us", env=env_uS)

# ensure the dependency
stack_uS.add_dependency(stack_jP)

# get remote parameters by path from SSM parameter store
parameters = RemoteParameters(stack_uS, "Parameters",
    path=parameter_path,
    region=stack_jP.region
)

foo1 = parameters.get(f"{parameterPath}/foo1")
foo2 = parameters.get(f"{parameterPath}/foo2")
foo3 = parameters.get(f"{parameterPath}/foo3")

cdk.CfnOutput(stack_uS, "foo1Output", value=foo1)
cdk.CfnOutput(stack_uS, "foo2Output", value=foo2)
cdk.CfnOutput(stack_uS, "foo3Output", value=foo3)
```

## #2 - Stacks from differnt accounts and different regions

Similar to the case above, now we are running seperate stacks in seperate account/region.  We will need to pass a `role` to the `RemoteParameters` construct to get all the parameters from remote.

![](images/remote-param-2.svg)

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
env_jP = {"region": "ap-northeast-1", "account": "111111111111"}
env_uS = {"region": "us-west-2", "account": "222222222222"}

# first stack in JP
producer_stack_name = "demo-stack-jp"
stack_jP = cdk.Stack(app, producer_stack_name, env=env_jP)
parameter_path = f"/{envJP.account}/{envJP.region}/{producerStackName}"

ssm.StringParameter(stack_jP, "foo1",
    parameter_name=f"{parameterPath}/foo1",
    string_value="bar1"
)
ssm.StringParameter(stack_jP, "foo2",
    parameter_name=f"{parameterPath}/foo2",
    string_value="bar2"
)
ssm.StringParameter(stack_jP, "foo3",
    parameter_name=f"{parameterPath}/foo3",
    string_value="bar3"
)

# allow US account to assume this readonly role to get parameters
cdk_read_only_role = iam.Role(stack_jP, "readOnlyRole",
    assumed_by=iam.AccountPrincipal(env_uS.account),
    role_name=PhysicalName.GENERATE_IF_NEEDED,
    managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")]
)

# second stack in US
stack_uS = cdk.Stack(app, "demo-stack-us", env=env_uS)

# ensure the dependency
stack_uS.add_dependency(stack_jP)

# get remote parameters by path from SSM parameter store
parameters = RemoteParameters(stack_uS, "Parameters",
    path=parameter_path,
    region=stack_jP.region,
    # assume this role for cross-account parameters
    role=iam.Role.from_role_arn(stack_uS, "readOnlyRole", cdk_read_only_role.role_arn)
)

foo1 = parameters.get(f"{parameterPath}/foo1")
foo2 = parameters.get(f"{parameterPath}/foo2")
foo3 = parameters.get(f"{parameterPath}/foo3")

cdk.CfnOutput(stack_uS, "foo1Output", value=foo1)
cdk.CfnOutput(stack_uS, "foo2Output", value=foo2)
cdk.CfnOutput(stack_uS, "foo3Output", value=foo3)
```

## #3 - dedicated account for a centralized parameter store

The parameters are stored in a centralized account/region and previously provisioned as a state-of-truth configuration store. All other stacks from different account/region are consuming the parameters from remote.

This scenario is pretty much like #2. The difference is that there's a dedicated account for centralized parameter store being shared across all other accounts.

![](images/remote-param-3.svg)

You will need create `RemoteParameters` for all the consuming stacks like:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# for StackUS
RemoteParameters(stack_uS, "Parameters",
    path=parameter_path,
    region="eu-central-1",
    # assume this role for cross-account parameters
    role=iam.Role.from_role_arn(stack_uS, "readOnlyRole", shared_read_only_role_arn)
)

# for StackJP
RemoteParameters(stack_jP, "Parameters",
    path=parameter_path,
    region="eu-central-1",
    # assume this role for cross-account parameters
    role=iam.Role.from_role_arn(stack_jP, "readOnlyRole", shared_read_only_role_arn)
)
```

## Tools for multi-account deployment

You will need to install [cdk-assume-role-credential-plugin](https://github.com/aws-samples/cdk-assume-role-credential-plugin) so you can deploy stacks from different accounts. Read this [blog post](https://aws.amazon.com/tw/blogs/devops/cdk-credential-plugin/) to setup this plugin.

## Limitation

1. At this moment, the `RemoteParameters` construct only support the `String` data type from parameter store.
2. Max number of parameters is `100`. Will make it configurable in the future PR when required.
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

import aws_cdk.aws_iam
import aws_cdk.core


class RemoteOutputs(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-remote-stack.RemoteOutputs",
):
    '''Represents the RemoteOutputs of the remote CDK stack.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        stack: aws_cdk.core.Stack,
        always_update: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param stack: The remote CDK stack to get the outputs from.
        :param always_update: Indicate whether always update the custom resource to get the new stack output. Default: true
        '''
        props = RemoteOutputsProps(stack=stack, always_update=always_update)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="get")
    def get(self, key: builtins.str) -> builtins.str:
        '''Get the attribute value from the outputs.

        :param key: output key.
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "get", [key]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputs")
    def outputs(self) -> aws_cdk.core.CustomResource:
        '''The outputs from the remote stack.'''
        return typing.cast(aws_cdk.core.CustomResource, jsii.get(self, "outputs"))


@jsii.data_type(
    jsii_type="cdk-remote-stack.RemoteOutputsProps",
    jsii_struct_bases=[],
    name_mapping={"stack": "stack", "always_update": "alwaysUpdate"},
)
class RemoteOutputsProps:
    def __init__(
        self,
        *,
        stack: aws_cdk.core.Stack,
        always_update: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties of the RemoteOutputs.

        :param stack: The remote CDK stack to get the outputs from.
        :param always_update: Indicate whether always update the custom resource to get the new stack output. Default: true
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "stack": stack,
        }
        if always_update is not None:
            self._values["always_update"] = always_update

    @builtins.property
    def stack(self) -> aws_cdk.core.Stack:
        '''The remote CDK stack to get the outputs from.'''
        result = self._values.get("stack")
        assert result is not None, "Required property 'stack' is missing"
        return typing.cast(aws_cdk.core.Stack, result)

    @builtins.property
    def always_update(self) -> typing.Optional[builtins.bool]:
        '''Indicate whether always update the custom resource to get the new stack output.

        :default: true
        '''
        result = self._values.get("always_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RemoteOutputsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RemoteParameters(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-remote-stack.RemoteParameters",
):
    '''Represents the RemoteParameters of the remote CDK stack.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        path: builtins.str,
        region: builtins.str,
        always_update: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param path: The parameter path.
        :param region: The region code of the remote stack.
        :param always_update: Indicate whether always update the custom resource to get the new stack output. Default: true
        :param role: The assumed role used to get remote parameters.
        '''
        props = RemoteParametersProps(
            path=path, region=region, always_update=always_update, role=role
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="get")
    def get(self, key: builtins.str) -> builtins.str:
        '''Get the parameter.

        :param key: output key.
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "get", [key]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> aws_cdk.core.CustomResource:
        '''The parameters in the SSM parameter store for the remote stack.'''
        return typing.cast(aws_cdk.core.CustomResource, jsii.get(self, "parameters"))


@jsii.data_type(
    jsii_type="cdk-remote-stack.RemoteParametersProps",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "region": "region",
        "always_update": "alwaysUpdate",
        "role": "role",
    },
)
class RemoteParametersProps:
    def __init__(
        self,
        *,
        path: builtins.str,
        region: builtins.str,
        always_update: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''Properties of the RemoteParameters.

        :param path: The parameter path.
        :param region: The region code of the remote stack.
        :param always_update: Indicate whether always update the custom resource to get the new stack output. Default: true
        :param role: The assumed role used to get remote parameters.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
            "region": region,
        }
        if always_update is not None:
            self._values["always_update"] = always_update
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def path(self) -> builtins.str:
        '''The parameter path.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''The region code of the remote stack.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def always_update(self) -> typing.Optional[builtins.bool]:
        '''Indicate whether always update the custom resource to get the new stack output.

        :default: true
        '''
        result = self._values.get("always_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The assumed role used to get remote parameters.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RemoteParametersProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RemoteOutputs",
    "RemoteOutputsProps",
    "RemoteParameters",
    "RemoteParametersProps",
]

publication.publish()
