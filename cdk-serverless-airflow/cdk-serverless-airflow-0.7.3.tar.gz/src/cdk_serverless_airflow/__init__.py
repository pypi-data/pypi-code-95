'''
[![Build](https://github.com/readybuilderone/serverless-airflow/actions/workflows/build.yml/badge.svg)](https://github.com/readybuilderone/serverless-airflow/actions/workflows/build.yml)
[![NPM version](https://badge.fury.io/js/cdk-serverless-airflow.svg)](https://badge.fury.io/js/cdk-serverless-airflow)
[![PyPI version](https://badge.fury.io/py/cdk-serverless-airflow.svg)](https://badge.fury.io/py/cdk-serverless-airflow)

# `CDK Serverless Airflow`

CDK construct library that allows you to create [Apache Airflow](https://airflow.apache.org/) on AWS in TypeScript or Python

# Architecture

![architecture](./assets/01-serverless-airflow-on-aws-architecture.svg)

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
import cdk_serverless_airflow as airflow

app = cdk.App()
env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}
stack = cdk.Stack(app, "airflow-stack",
    env=env
)
airflow.Airflow(stack, "Airflow")
```

# Airflow Dashboard

> Default Credential: user/bitnami

![airflow-dashboard](./assets/04-airflow-dashboard.jpg)

# AWS China Regions

AWS China regions `cn-north-1` and `cn-northwest-1` are supported by this Library.

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk.core


class Airflow(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-serverless-airflow.Airflow",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        airflow_fernet_key: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        db_name: typing.Optional[builtins.str] = None,
        ecscluster_name: typing.Optional[builtins.str] = None,
        redis_name: typing.Optional[builtins.str] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param airflow_fernet_key: 
        :param bucket_name: 
        :param db_name: 
        :param ecscluster_name: 
        :param redis_name: 
        :param vpc_name: 
        '''
        props = AirflowProps(
            airflow_fernet_key=airflow_fernet_key,
            bucket_name=bucket_name,
            db_name=db_name,
            ecscluster_name=ecscluster_name,
            redis_name=redis_name,
            vpc_name=vpc_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-serverless-airflow.AirflowProps",
    jsii_struct_bases=[],
    name_mapping={
        "airflow_fernet_key": "airflowFernetKey",
        "bucket_name": "bucketName",
        "db_name": "dbName",
        "ecscluster_name": "ecsclusterName",
        "redis_name": "redisName",
        "vpc_name": "vpcName",
    },
)
class AirflowProps:
    def __init__(
        self,
        *,
        airflow_fernet_key: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        db_name: typing.Optional[builtins.str] = None,
        ecscluster_name: typing.Optional[builtins.str] = None,
        redis_name: typing.Optional[builtins.str] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param airflow_fernet_key: 
        :param bucket_name: 
        :param db_name: 
        :param ecscluster_name: 
        :param redis_name: 
        :param vpc_name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if airflow_fernet_key is not None:
            self._values["airflow_fernet_key"] = airflow_fernet_key
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if db_name is not None:
            self._values["db_name"] = db_name
        if ecscluster_name is not None:
            self._values["ecscluster_name"] = ecscluster_name
        if redis_name is not None:
            self._values["redis_name"] = redis_name
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name

    @builtins.property
    def airflow_fernet_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("airflow_fernet_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecscluster_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ecscluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redis_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("redis_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AirflowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Airflow",
    "AirflowProps",
]

publication.publish()
