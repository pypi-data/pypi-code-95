'''
[![NPM version](https://badge.fury.io/js/cdk-serverless-lamp.svg)](https://badge.fury.io/js/cdk-serverless-lamp)
[![PyPI version](https://badge.fury.io/py/cdk-serverless-lamp.svg)](https://badge.fury.io/py/cdk-serverless-lamp)
![Build](https://github.com/aws-samples/cdk-serverless-lamp/workflows/Build/badge.svg)

# Welcome to cdk-serverless-lamp

`cdk-serverless-lamp` is a JSII construct library for AWS CDK that allows you to deploy the [New Serverless LAMP Stack](https://aws.amazon.com/tw/blogs/compute/introducing-the-new-serverless-lamp-stack/) running PHP Laravel Apps by specifying the local `laravel` directory.

By deploying the `ServerlessLaravel` and `DatabaseCluster`, the following resources will be created:

1. Amazon API Gateway HTTP API
2. AWS Lambda custom runtime with [Bref runtime](https://bref.sh/docs/runtimes/) support
3. Amazon Aurora for MySQL database cluster with RDS proxy enabled

## Howto

Create a new Laravel project with AWS CDK

```sh
$ mkdir serverless-lamp && cd serverless-lamp
# create cdk and codebase directories for AWS CDK and Laravel project
$ mkdir cdk codebase
# create the new Laravel project with docker
$ docker run --rm -ti \
  --volume $PWD:/app \
  composer create-project --prefer-dist laravel/laravel ./codebase
# install bref/bref and bref/laravel-bridge in the vendor
$ cd codebase
$ docker run --rm -ti \
  --volume $PWD:/app \
  composer require bref/bref bref/laravel-bridge
# initialize the AWS CDK project
$ cd ../cdk
$ cdk init -l typescript
# install the cdk-severless-lamp npm module
$ yarn add cdk-serverless-lamp
```

Now your directories should look like this:

```
.
├── cdk
└── codebase
```

where `cdk` is for the AWS CDK and `codebase` for Laravel project.

# AWS CDK sample

Building your serverless Laravel with `ServerlessLaravel` construct:

Update `./cdk/lib/cdk-stack.ts`

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
import path as path
from cdk_serverless_lamp import ServerlessLaravel

class CdkStack(cdk.Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        ServerlessLaravel(self, "ServerlessLaravel",
            bref_layer_version="arn:aws:lambda:us-east-1:209497400698:layer:php-74-fpm:12",
            laravel_path=path.join(__dirname, "../../codebase")
        )
```

deploy the CDK stack:

```sh
# see the difference before the deployment
$ cdk diff
# deploy it
$ cdk deploy
```

On deploy complete, the API Gateway URL will be returned in the Output. Click the URL and you will see the Laravel landing page:

![laravel-welcome](./images/laravel.png)

## Amazon Aurora support

Use `DatabaseCluster` to create the your database cluster:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
from aws_cdk.aws_ec2 import InstanceType, Vpc
import path as path
from cdk_serverless_lamp import ServerlessLaravel, DatabaseCluster

class CdkStack(cdk.Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        vpc = Vpc(self, "Vpc", max_azs=3, nat_gateways=1)

        # the DatabaseCluster sharing the same vpc with the ServerlessLaravel
        db = DatabaseCluster(self, "DatabaseCluster",
            vpc=vpc,
            instance_type=InstanceType("t3.small"),
            rds_proxy=True
        )

        # the ServerlessLaravel
        ServerlessLaravel(self, "ServerlessLaravel",
            bref_layer_version="arn:aws:lambda:us-east-1:209497400698:layer:php-74-fpm:12",
            laravel_path=path.join(__dirname, "../../codebase"),
            vpc=vpc,
            database_config={
                "writer_endpoint": db.rds_proxy.endpoint
            }
        )
```

## Local Development

Create `docker-compose.yml` with the following content:

```docker-compose
version: "3.5"
services:
  web:
    image: bref/fpm-dev-gateway
    ports:
      - "8000:80"
    volumes:
      - ./laravel:/var/task
    depends_on:
      - php
    environment:
      HANDLER: public/index.php
  php:
    image: bref/php-74-fpm-dev
    volumes:
      - ./laravel:/var/task
```

and run this command `docker-compose up -d` and now you can access [http://localhost:8000](http://localhost:8000).

*(more information can be found in [bref documentation](https://bref.sh/docs/local-development.html))*
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
import aws_cdk.aws_lambda
import aws_cdk.aws_rds
import aws_cdk.aws_secretsmanager
import aws_cdk.core


class DatabaseCluster(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-serverless-lamp.DatabaseCluster",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        instance_capacity: typing.Optional[jsii.Number] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        master_user_name: typing.Optional[builtins.str] = None,
        rds_proxy: typing.Optional[builtins.bool] = None,
        rds_proxy_options: typing.Optional[aws_cdk.aws_rds.DatabaseProxyOptions] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC for the DatabaseCluster.
        :param engine: database cluster engine. Default: AURORA_MYSQL
        :param instance_capacity: How many replicas/instances to create. Has to be at least 1. Default: 1
        :param instance_type: instance type of the cluster. Default: - t3.medium (or, more precisely, db.t3.medium)
        :param master_user_name: master username. Default: admin
        :param rds_proxy: enable the Amazon RDS proxy. Default: true
        :param rds_proxy_options: RDS Proxy Options.
        '''
        props = DatabaseProps(
            vpc=vpc,
            engine=engine,
            instance_capacity=instance_capacity,
            instance_type=instance_type,
            master_user_name=master_user_name,
            rds_proxy=rds_proxy,
            rds_proxy_options=rds_proxy_options,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterPassword")
    def master_password(self) -> aws_cdk.aws_secretsmanager.ISecret:
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "masterPassword"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUser")
    def master_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterUser"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsProxy")
    def rds_proxy(self) -> typing.Optional[aws_cdk.aws_rds.DatabaseProxy]:
        return typing.cast(typing.Optional[aws_cdk.aws_rds.DatabaseProxy], jsii.get(self, "rdsProxy"))


@jsii.data_type(
    jsii_type="cdk-serverless-lamp.DatabaseConfig",
    jsii_struct_bases=[],
    name_mapping={
        "writer_endpoint": "writerEndpoint",
        "master_user_name": "masterUserName",
        "master_user_password_secret": "masterUserPasswordSecret",
        "reader_endpoint": "readerEndpoint",
    },
)
class DatabaseConfig:
    def __init__(
        self,
        *,
        writer_endpoint: builtins.str,
        master_user_name: typing.Optional[builtins.str] = None,
        master_user_password_secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
        reader_endpoint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param writer_endpoint: The DB writer endpoint.
        :param master_user_name: The DB master username.
        :param master_user_password_secret: The DB master password secret.
        :param reader_endpoint: The DB reader endpoint.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "writer_endpoint": writer_endpoint,
        }
        if master_user_name is not None:
            self._values["master_user_name"] = master_user_name
        if master_user_password_secret is not None:
            self._values["master_user_password_secret"] = master_user_password_secret
        if reader_endpoint is not None:
            self._values["reader_endpoint"] = reader_endpoint

    @builtins.property
    def writer_endpoint(self) -> builtins.str:
        '''The DB writer endpoint.'''
        result = self._values.get("writer_endpoint")
        assert result is not None, "Required property 'writer_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def master_user_name(self) -> typing.Optional[builtins.str]:
        '''The DB master username.'''
        result = self._values.get("master_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_user_password_secret(
        self,
    ) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''The DB master password secret.'''
        result = self._values.get("master_user_password_secret")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], result)

    @builtins.property
    def reader_endpoint(self) -> typing.Optional[builtins.str]:
        '''The DB reader endpoint.'''
        result = self._values.get("reader_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-serverless-lamp.DatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "engine": "engine",
        "instance_capacity": "instanceCapacity",
        "instance_type": "instanceType",
        "master_user_name": "masterUserName",
        "rds_proxy": "rdsProxy",
        "rds_proxy_options": "rdsProxyOptions",
    },
)
class DatabaseProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        instance_capacity: typing.Optional[jsii.Number] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        master_user_name: typing.Optional[builtins.str] = None,
        rds_proxy: typing.Optional[builtins.bool] = None,
        rds_proxy_options: typing.Optional[aws_cdk.aws_rds.DatabaseProxyOptions] = None,
    ) -> None:
        '''
        :param vpc: The VPC for the DatabaseCluster.
        :param engine: database cluster engine. Default: AURORA_MYSQL
        :param instance_capacity: How many replicas/instances to create. Has to be at least 1. Default: 1
        :param instance_type: instance type of the cluster. Default: - t3.medium (or, more precisely, db.t3.medium)
        :param master_user_name: master username. Default: admin
        :param rds_proxy: enable the Amazon RDS proxy. Default: true
        :param rds_proxy_options: RDS Proxy Options.
        '''
        if isinstance(rds_proxy_options, dict):
            rds_proxy_options = aws_cdk.aws_rds.DatabaseProxyOptions(**rds_proxy_options)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if engine is not None:
            self._values["engine"] = engine
        if instance_capacity is not None:
            self._values["instance_capacity"] = instance_capacity
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if master_user_name is not None:
            self._values["master_user_name"] = master_user_name
        if rds_proxy is not None:
            self._values["rds_proxy"] = rds_proxy
        if rds_proxy_options is not None:
            self._values["rds_proxy_options"] = rds_proxy_options

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC for the DatabaseCluster.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def engine(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''database cluster engine.

        :default: AURORA_MYSQL
        '''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def instance_capacity(self) -> typing.Optional[jsii.Number]:
        '''How many replicas/instances to create.

        Has to be at least 1.

        :default: 1
        '''
        result = self._values.get("instance_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''instance type of the cluster.

        :default: - t3.medium (or, more precisely, db.t3.medium)
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def master_user_name(self) -> typing.Optional[builtins.str]:
        '''master username.

        :default: admin
        '''
        result = self._values.get("master_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rds_proxy(self) -> typing.Optional[builtins.bool]:
        '''enable the Amazon RDS proxy.

        :default: true
        '''
        result = self._values.get("rds_proxy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rds_proxy_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_rds.DatabaseProxyOptions]:
        '''RDS Proxy Options.'''
        result = self._values.get("rds_proxy_options")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.DatabaseProxyOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerlessApi(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-serverless-lamp.ServerlessApi",
):
    '''Use ``ServerlessApi`` to create the serverless API resource.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bref_layer_version: builtins.str,
        database_config: typing.Optional[DatabaseConfig] = None,
        handler: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
        lambda_code_path: typing.Optional[builtins.str] = None,
        rds_proxy: typing.Optional[aws_cdk.aws_rds.IDatabaseProxy] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bref_layer_version: AWS Lambda layer version from the Bref runtime. e.g. arn:aws:lambda:us-west-1:209497400698:layer:php-74-fpm:12 check the latest runtime verion arn at https://bref.sh/docs/runtimes/
        :param database_config: Database configurations.
        :param handler: custom lambda function for the API. Default: - A Lambda function with Lavavel and Bref support will be created
        :param lambda_code_path: custom lambda code asset path. Default: - DEFAULT_LAMBDA_ASSET_PATH
        :param rds_proxy: RDS Proxy for the Lambda function. Default: - no db proxy
        :param vpc: The VPC for this stack.
        '''
        props = ServerlessApiProps(
            bref_layer_version=bref_layer_version,
            database_config=database_config,
            handler=handler,
            lambda_code_path=lambda_code_path,
            rds_proxy=rds_proxy,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-serverless-lamp.ServerlessApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "bref_layer_version": "brefLayerVersion",
        "database_config": "databaseConfig",
        "handler": "handler",
        "lambda_code_path": "lambdaCodePath",
        "rds_proxy": "rdsProxy",
        "vpc": "vpc",
    },
)
class ServerlessApiProps:
    def __init__(
        self,
        *,
        bref_layer_version: builtins.str,
        database_config: typing.Optional[DatabaseConfig] = None,
        handler: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
        lambda_code_path: typing.Optional[builtins.str] = None,
        rds_proxy: typing.Optional[aws_cdk.aws_rds.IDatabaseProxy] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''Construct properties for ``ServerlessApi``.

        :param bref_layer_version: AWS Lambda layer version from the Bref runtime. e.g. arn:aws:lambda:us-west-1:209497400698:layer:php-74-fpm:12 check the latest runtime verion arn at https://bref.sh/docs/runtimes/
        :param database_config: Database configurations.
        :param handler: custom lambda function for the API. Default: - A Lambda function with Lavavel and Bref support will be created
        :param lambda_code_path: custom lambda code asset path. Default: - DEFAULT_LAMBDA_ASSET_PATH
        :param rds_proxy: RDS Proxy for the Lambda function. Default: - no db proxy
        :param vpc: The VPC for this stack.
        '''
        if isinstance(database_config, dict):
            database_config = DatabaseConfig(**database_config)
        self._values: typing.Dict[str, typing.Any] = {
            "bref_layer_version": bref_layer_version,
        }
        if database_config is not None:
            self._values["database_config"] = database_config
        if handler is not None:
            self._values["handler"] = handler
        if lambda_code_path is not None:
            self._values["lambda_code_path"] = lambda_code_path
        if rds_proxy is not None:
            self._values["rds_proxy"] = rds_proxy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def bref_layer_version(self) -> builtins.str:
        '''AWS Lambda layer version from the Bref runtime.

        e.g. arn:aws:lambda:us-west-1:209497400698:layer:php-74-fpm:12
        check the latest runtime verion arn at https://bref.sh/docs/runtimes/
        '''
        result = self._values.get("bref_layer_version")
        assert result is not None, "Required property 'bref_layer_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_config(self) -> typing.Optional[DatabaseConfig]:
        '''Database configurations.'''
        result = self._values.get("database_config")
        return typing.cast(typing.Optional[DatabaseConfig], result)

    @builtins.property
    def handler(self) -> typing.Optional[aws_cdk.aws_lambda.IFunction]:
        '''custom lambda function for the API.

        :default: - A Lambda function with Lavavel and Bref support will be created
        '''
        result = self._values.get("handler")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IFunction], result)

    @builtins.property
    def lambda_code_path(self) -> typing.Optional[builtins.str]:
        '''custom lambda code asset path.

        :default: - DEFAULT_LAMBDA_ASSET_PATH
        '''
        result = self._values.get("lambda_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rds_proxy(self) -> typing.Optional[aws_cdk.aws_rds.IDatabaseProxy]:
        '''RDS Proxy for the Lambda function.

        :default: - no db proxy
        '''
        result = self._values.get("rds_proxy")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IDatabaseProxy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''The VPC for this stack.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerlessLaravel(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-serverless-lamp.ServerlessLaravel",
):
    '''Use ``ServerlessLaravel`` to create the serverless Laravel resource.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        laravel_path: builtins.str,
        bref_layer_version: builtins.str,
        database_config: typing.Optional[DatabaseConfig] = None,
        handler: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
        lambda_code_path: typing.Optional[builtins.str] = None,
        rds_proxy: typing.Optional[aws_cdk.aws_rds.IDatabaseProxy] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param laravel_path: path to your local laravel directory with bref.
        :param bref_layer_version: AWS Lambda layer version from the Bref runtime. e.g. arn:aws:lambda:us-west-1:209497400698:layer:php-74-fpm:12 check the latest runtime verion arn at https://bref.sh/docs/runtimes/
        :param database_config: Database configurations.
        :param handler: custom lambda function for the API. Default: - A Lambda function with Lavavel and Bref support will be created
        :param lambda_code_path: custom lambda code asset path. Default: - DEFAULT_LAMBDA_ASSET_PATH
        :param rds_proxy: RDS Proxy for the Lambda function. Default: - no db proxy
        :param vpc: The VPC for this stack.
        '''
        props = ServerlessLaravelProps(
            laravel_path=laravel_path,
            bref_layer_version=bref_layer_version,
            database_config=database_config,
            handler=handler,
            lambda_code_path=lambda_code_path,
            rds_proxy=rds_proxy,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-serverless-lamp.ServerlessLaravelProps",
    jsii_struct_bases=[ServerlessApiProps],
    name_mapping={
        "bref_layer_version": "brefLayerVersion",
        "database_config": "databaseConfig",
        "handler": "handler",
        "lambda_code_path": "lambdaCodePath",
        "rds_proxy": "rdsProxy",
        "vpc": "vpc",
        "laravel_path": "laravelPath",
    },
)
class ServerlessLaravelProps(ServerlessApiProps):
    def __init__(
        self,
        *,
        bref_layer_version: builtins.str,
        database_config: typing.Optional[DatabaseConfig] = None,
        handler: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
        lambda_code_path: typing.Optional[builtins.str] = None,
        rds_proxy: typing.Optional[aws_cdk.aws_rds.IDatabaseProxy] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        laravel_path: builtins.str,
    ) -> None:
        '''Construct properties for ``ServerlessLaravel``.

        :param bref_layer_version: AWS Lambda layer version from the Bref runtime. e.g. arn:aws:lambda:us-west-1:209497400698:layer:php-74-fpm:12 check the latest runtime verion arn at https://bref.sh/docs/runtimes/
        :param database_config: Database configurations.
        :param handler: custom lambda function for the API. Default: - A Lambda function with Lavavel and Bref support will be created
        :param lambda_code_path: custom lambda code asset path. Default: - DEFAULT_LAMBDA_ASSET_PATH
        :param rds_proxy: RDS Proxy for the Lambda function. Default: - no db proxy
        :param vpc: The VPC for this stack.
        :param laravel_path: path to your local laravel directory with bref.
        '''
        if isinstance(database_config, dict):
            database_config = DatabaseConfig(**database_config)
        self._values: typing.Dict[str, typing.Any] = {
            "bref_layer_version": bref_layer_version,
            "laravel_path": laravel_path,
        }
        if database_config is not None:
            self._values["database_config"] = database_config
        if handler is not None:
            self._values["handler"] = handler
        if lambda_code_path is not None:
            self._values["lambda_code_path"] = lambda_code_path
        if rds_proxy is not None:
            self._values["rds_proxy"] = rds_proxy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def bref_layer_version(self) -> builtins.str:
        '''AWS Lambda layer version from the Bref runtime.

        e.g. arn:aws:lambda:us-west-1:209497400698:layer:php-74-fpm:12
        check the latest runtime verion arn at https://bref.sh/docs/runtimes/
        '''
        result = self._values.get("bref_layer_version")
        assert result is not None, "Required property 'bref_layer_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_config(self) -> typing.Optional[DatabaseConfig]:
        '''Database configurations.'''
        result = self._values.get("database_config")
        return typing.cast(typing.Optional[DatabaseConfig], result)

    @builtins.property
    def handler(self) -> typing.Optional[aws_cdk.aws_lambda.IFunction]:
        '''custom lambda function for the API.

        :default: - A Lambda function with Lavavel and Bref support will be created
        '''
        result = self._values.get("handler")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IFunction], result)

    @builtins.property
    def lambda_code_path(self) -> typing.Optional[builtins.str]:
        '''custom lambda code asset path.

        :default: - DEFAULT_LAMBDA_ASSET_PATH
        '''
        result = self._values.get("lambda_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rds_proxy(self) -> typing.Optional[aws_cdk.aws_rds.IDatabaseProxy]:
        '''RDS Proxy for the Lambda function.

        :default: - no db proxy
        '''
        result = self._values.get("rds_proxy")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IDatabaseProxy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''The VPC for this stack.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def laravel_path(self) -> builtins.str:
        '''path to your local laravel directory with bref.'''
        result = self._values.get("laravel_path")
        assert result is not None, "Required property 'laravel_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessLaravelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabaseCluster",
    "DatabaseConfig",
    "DatabaseProps",
    "ServerlessApi",
    "ServerlessApiProps",
    "ServerlessLaravel",
    "ServerlessLaravelProps",
]

publication.publish()
