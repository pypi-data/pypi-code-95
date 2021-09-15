'''
[![NPM version](https://badge.fury.io/js/cdk-keycloak.svg)](https://badge.fury.io/js/cdk-keycloak)
[![PyPI version](https://badge.fury.io/py/cdk-keycloak.svg)](https://badge.fury.io/py/cdk-keycloak)
![Release](https://github.com/pahud/cdk-keycloak/workflows/Release/badge.svg?branch=main)

# `cdk-keycloak`

CDK construct library that allows you to create [KeyCloak](https://www.keycloak.org/) on AWS in TypeScript or Python

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_keycloak import KeyCloak

app = cdk.App()

env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

stack = cdk.Stack(app, "keycloak-demo", env=env)
KeyCloak(stack, "KeyCloak",
    certificate_arn="arn:aws:acm:us-east-1:123456789012:certificate/293cf875-ca98-4c2e-a797-e1cf6df2553c"
)
```

# Aurora Serverless support

The `KeyCloak` construct provisions the **Amaozn RDS cluster for MySQL** with **2** database instances under the hood, to opt in **Amazon Aurora Serverless**, use `auroraServerless` to opt in Amazon Aurora Serverless cluster. Please note only some regions are supported, check [Supported features in Amazon Aurora by AWS Region and Aurora DB engine](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraFeaturesRegionsDBEngines.grids.html) for availability.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
KeyCloak(stack, "KeyCloak",
    certificate_arn=certificate_arn,
    aurora_serverless=True
)
```

Behind the scene, a default RDS cluster for MySQL with 2 database instances will be created.

# Opt-in for Single RDS instance

To create single RDS instance for your testing or development environment, use `singleDbInstance` to turn on the
single db instance deployment.

Plesae note this is not recommended for production environment.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
KeyCloak(stack, "KeyCloak",
    certificate_arn=certificate_arn,
    single_db_instance=True
)
```

# Service Auto Scaling

Define `autoScaleTask` for the ecs service task autoscaling. For example:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
KeyCloak(stack, "KeyCloak",
    aurora_serverless=True,
    node_count=2,
    auto_scale_task={
        "min": 2,
        "max": 10,
        "target_cpu_utilization": 60
    }
)
```

# Deploy in existing Vpc Subnets

You can deploy the workload in the existing Vpc and subnets. The `publicSubnets` are for the ALB, `privateSubnets` for the keycloak container tasks and `databaseSubnets` for the database.

The best practice is to specify isolated subnets for `databaseSubnets`, however, in some cases might have no existing isolates subnets then the private subnets are also acceptable.

Consider the sample below:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
KeyCloak(stack, "KeyCloak",
    certificate_arn="arn:aws:acm:us-east-1:123456789012:certificate/293cf875-ca98-4c2e-a797-e1cf6df2553c",
    vpc=ec2.Vpc.from_lookup(stack, "Vpc", vpc_id="vpc-0417e46d"),
    public_subnets={
        "subnets": [
            ec2.Subnet.from_subnet_id(stack, "pub-1a", "subnet-5bbe7b32"),
            ec2.Subnet.from_subnet_id(stack, "pub-1b", "subnet-0428367c"),
            ec2.Subnet.from_subnet_id(stack, "pub-1c", "subnet-1586a75f")
        ]
    },
    private_subnets={
        "subnets": [
            ec2.Subnet.from_subnet_id(stack, "priv-1a", "subnet-0e9460dbcfc4cf6ee"),
            ec2.Subnet.from_subnet_id(stack, "priv-1b", "subnet-0562f666bdf5c29af"),
            ec2.Subnet.from_subnet_id(stack, "priv-1c", "subnet-00ab15c0022872f06")
        ]
    },
    database_subnets={
        "subnets": [
            ec2.Subnet.from_subnet_id(stack, "db-1a", "subnet-0e9460dbcfc4cf6ee"),
            ec2.Subnet.from_subnet_id(stack, "db-1b", "subnet-0562f666bdf5c29af"),
            ec2.Subnet.from_subnet_id(stack, "db-1c", "subnet-00ab15c0022872f06")
        ]
    }
)
```

# AWS China Regions

This library support AWS China regions `cn-north-1` and `cn-northwest-1` and will auto select local docker image mirror to accelerate the image pulling. You don't have to do anything.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

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

import aws_cdk.aws_certificatemanager
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_rds
import aws_cdk.aws_secretsmanager
import aws_cdk.core


@jsii.data_type(
    jsii_type="cdk-keycloak.AutoScaleTask",
    jsii_struct_bases=[],
    name_mapping={
        "max": "max",
        "min": "min",
        "target_cpu_utilization": "targetCpuUtilization",
    },
)
class AutoScaleTask:
    def __init__(
        self,
        *,
        max: typing.Optional[jsii.Number] = None,
        min: typing.Optional[jsii.Number] = None,
        target_cpu_utilization: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''The ECS task autoscaling definition.

        :param max: The maximal count of the task number. Default: - min + 5
        :param min: The minimal count of the task number. Default: - nodeCount
        :param target_cpu_utilization: The target cpu utilization for the service autoscaling. Default: 75
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max is not None:
            self._values["max"] = max
        if min is not None:
            self._values["min"] = min
        if target_cpu_utilization is not None:
            self._values["target_cpu_utilization"] = target_cpu_utilization

    @builtins.property
    def max(self) -> typing.Optional[jsii.Number]:
        '''The maximal count of the task number.

        :default: - min + 5
        '''
        result = self._values.get("max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min(self) -> typing.Optional[jsii.Number]:
        '''The minimal count of the task number.

        :default: - nodeCount
        '''
        result = self._values.get("min")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_cpu_utilization(self) -> typing.Optional[jsii.Number]:
        '''The target cpu utilization for the service autoscaling.

        :default: 75
        '''
        result = self._values.get("target_cpu_utilization")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScaleTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerService(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-keycloak.ContainerService",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
        database: "Database",
        keycloak_secret: aws_cdk.aws_secretsmanager.ISecret,
        vpc: aws_cdk.aws_ec2.IVpc,
        auto_scale_task: typing.Optional[AutoScaleTask] = None,
        bastion: typing.Optional[builtins.bool] = None,
        circuit_breaker: typing.Optional[builtins.bool] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_count: typing.Optional[jsii.Number] = None,
        private_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        public_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        stickiness_cookie_duration: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificate: The ACM certificate.
        :param database: The RDS database for the service.
        :param keycloak_secret: The secrets manager secret for the keycloak.
        :param vpc: The VPC for the service.
        :param auto_scale_task: Autoscaling for the ECS Service. Default: - no ecs service autoscaling
        :param bastion: Whether to create the bastion host. Default: false
        :param circuit_breaker: Whether to enable the ECS service deployment circuit breaker. Default: false
        :param env: The environment variables to pass to the keycloak container.
        :param node_count: Number of keycloak node in the cluster. Default: 1
        :param private_subnets: VPC subnets for keycloak service.
        :param public_subnets: VPC public subnets for ALB.
        :param stickiness_cookie_duration: The sticky session duration for the keycloak workload with ALB. Default: - one day
        '''
        props = ContainerServiceProps(
            certificate=certificate,
            database=database,
            keycloak_secret=keycloak_secret,
            vpc=vpc,
            auto_scale_task=auto_scale_task,
            bastion=bastion,
            circuit_breaker=circuit_breaker,
            env=env,
            node_count=node_count,
            private_subnets=private_subnets,
            public_subnets=public_subnets,
            stickiness_cookie_duration=stickiness_cookie_duration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> aws_cdk.aws_ecs.FargateService:
        return typing.cast(aws_cdk.aws_ecs.FargateService, jsii.get(self, "service"))


@jsii.data_type(
    jsii_type="cdk-keycloak.ContainerServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "database": "database",
        "keycloak_secret": "keycloakSecret",
        "vpc": "vpc",
        "auto_scale_task": "autoScaleTask",
        "bastion": "bastion",
        "circuit_breaker": "circuitBreaker",
        "env": "env",
        "node_count": "nodeCount",
        "private_subnets": "privateSubnets",
        "public_subnets": "publicSubnets",
        "stickiness_cookie_duration": "stickinessCookieDuration",
    },
)
class ContainerServiceProps:
    def __init__(
        self,
        *,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
        database: "Database",
        keycloak_secret: aws_cdk.aws_secretsmanager.ISecret,
        vpc: aws_cdk.aws_ec2.IVpc,
        auto_scale_task: typing.Optional[AutoScaleTask] = None,
        bastion: typing.Optional[builtins.bool] = None,
        circuit_breaker: typing.Optional[builtins.bool] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_count: typing.Optional[jsii.Number] = None,
        private_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        public_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        stickiness_cookie_duration: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param certificate: The ACM certificate.
        :param database: The RDS database for the service.
        :param keycloak_secret: The secrets manager secret for the keycloak.
        :param vpc: The VPC for the service.
        :param auto_scale_task: Autoscaling for the ECS Service. Default: - no ecs service autoscaling
        :param bastion: Whether to create the bastion host. Default: false
        :param circuit_breaker: Whether to enable the ECS service deployment circuit breaker. Default: false
        :param env: The environment variables to pass to the keycloak container.
        :param node_count: Number of keycloak node in the cluster. Default: 1
        :param private_subnets: VPC subnets for keycloak service.
        :param public_subnets: VPC public subnets for ALB.
        :param stickiness_cookie_duration: The sticky session duration for the keycloak workload with ALB. Default: - one day
        '''
        if isinstance(auto_scale_task, dict):
            auto_scale_task = AutoScaleTask(**auto_scale_task)
        if isinstance(private_subnets, dict):
            private_subnets = aws_cdk.aws_ec2.SubnetSelection(**private_subnets)
        if isinstance(public_subnets, dict):
            public_subnets = aws_cdk.aws_ec2.SubnetSelection(**public_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "certificate": certificate,
            "database": database,
            "keycloak_secret": keycloak_secret,
            "vpc": vpc,
        }
        if auto_scale_task is not None:
            self._values["auto_scale_task"] = auto_scale_task
        if bastion is not None:
            self._values["bastion"] = bastion
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if env is not None:
            self._values["env"] = env
        if node_count is not None:
            self._values["node_count"] = node_count
        if private_subnets is not None:
            self._values["private_subnets"] = private_subnets
        if public_subnets is not None:
            self._values["public_subnets"] = public_subnets
        if stickiness_cookie_duration is not None:
            self._values["stickiness_cookie_duration"] = stickiness_cookie_duration

    @builtins.property
    def certificate(self) -> aws_cdk.aws_certificatemanager.ICertificate:
        '''The ACM certificate.'''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, result)

    @builtins.property
    def database(self) -> "Database":
        '''The RDS database for the service.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast("Database", result)

    @builtins.property
    def keycloak_secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''The secrets manager secret for the keycloak.'''
        result = self._values.get("keycloak_secret")
        assert result is not None, "Required property 'keycloak_secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC for the service.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def auto_scale_task(self) -> typing.Optional[AutoScaleTask]:
        '''Autoscaling for the ECS Service.

        :default: - no ecs service autoscaling
        '''
        result = self._values.get("auto_scale_task")
        return typing.cast(typing.Optional[AutoScaleTask], result)

    @builtins.property
    def bastion(self) -> typing.Optional[builtins.bool]:
        '''Whether to create the bastion host.

        :default: false
        '''
        result = self._values.get("bastion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def circuit_breaker(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable the ECS service deployment circuit breaker.

        :default: false
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The environment variables to pass to the keycloak container.'''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def node_count(self) -> typing.Optional[jsii.Number]:
        '''Number of keycloak node in the cluster.

        :default: 1
        '''
        result = self._values.get("node_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def private_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnets for keycloak service.'''
        result = self._values.get("private_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def public_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC public subnets for ALB.'''
        result = self._values.get("public_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def stickiness_cookie_duration(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The sticky session duration for the keycloak workload with ALB.

        :default: - one day
        '''
        result = self._values.get("stickiness_cookie_duration")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Database(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-keycloak.Database",
):
    '''Represents the database instance or database cluster.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC for the database.
        :param aurora_serverless: enable aurora serverless. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_subnets: VPC subnets for database.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param instance_type: The database instance type. Default: r5.large
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        '''
        props = DatabaseProps(
            vpc=vpc,
            aurora_serverless=aurora_serverless,
            backup_retention=backup_retention,
            cluster_engine=cluster_engine,
            database_subnets=database_subnets,
            instance_engine=instance_engine,
            instance_type=instance_type,
            single_db_instance=single_db_instance,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpointHostname")
    def cluster_endpoint_hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterEndpointHostname"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "secret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-keycloak.DatabaseCofig",
    jsii_struct_bases=[],
    name_mapping={
        "connections": "connections",
        "endpoint": "endpoint",
        "identifier": "identifier",
        "secret": "secret",
    },
)
class DatabaseCofig:
    def __init__(
        self,
        *,
        connections: aws_cdk.aws_ec2.Connections,
        endpoint: builtins.str,
        identifier: builtins.str,
        secret: aws_cdk.aws_secretsmanager.ISecret,
    ) -> None:
        '''Database configuration.

        :param connections: The database connnections.
        :param endpoint: The endpoint address for the database.
        :param identifier: The databasae identifier.
        :param secret: The database secret.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "connections": connections,
            "endpoint": endpoint,
            "identifier": identifier,
            "secret": secret,
        }

    @builtins.property
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''The database connnections.'''
        result = self._values.get("connections")
        assert result is not None, "Required property 'connections' is missing"
        return typing.cast(aws_cdk.aws_ec2.Connections, result)

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''The endpoint address for the database.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identifier(self) -> builtins.str:
        '''The databasae identifier.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''The database secret.'''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseCofig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-keycloak.DatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "aurora_serverless": "auroraServerless",
        "backup_retention": "backupRetention",
        "cluster_engine": "clusterEngine",
        "database_subnets": "databaseSubnets",
        "instance_engine": "instanceEngine",
        "instance_type": "instanceType",
        "single_db_instance": "singleDbInstance",
    },
)
class DatabaseProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param vpc: The VPC for the database.
        :param aurora_serverless: enable aurora serverless. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_subnets: VPC subnets for database.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param instance_type: The database instance type. Default: r5.large
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        '''
        if isinstance(database_subnets, dict):
            database_subnets = aws_cdk.aws_ec2.SubnetSelection(**database_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if aurora_serverless is not None:
            self._values["aurora_serverless"] = aurora_serverless
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cluster_engine is not None:
            self._values["cluster_engine"] = cluster_engine
        if database_subnets is not None:
            self._values["database_subnets"] = database_subnets
        if instance_engine is not None:
            self._values["instance_engine"] = instance_engine
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if single_db_instance is not None:
            self._values["single_db_instance"] = single_db_instance

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC for the database.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def aurora_serverless(self) -> typing.Optional[builtins.bool]:
        '''enable aurora serverless.

        :default: false
        '''
        result = self._values.get("aurora_serverless")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''database backup retension.

        :default: - 7 days
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def cluster_engine(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''The database cluster engine.

        :default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        '''
        result = self._values.get("cluster_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def database_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnets for database.'''
        result = self._values.get("database_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def instance_engine(self) -> typing.Optional[aws_cdk.aws_rds.IInstanceEngine]:
        '''The database instance engine.

        :default: - MySQL 8.0.21
        '''
        result = self._values.get("instance_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IInstanceEngine], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''The database instance type.

        :default: r5.large
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def single_db_instance(self) -> typing.Optional[builtins.bool]:
        '''Whether to use single RDS instance rather than RDS cluster.

        Not recommended for production.

        :default: false
        '''
        result = self._values.get("single_db_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KeyCloak(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-keycloak.KeyCloak",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        certificate_arn: builtins.str,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        auto_scale_task: typing.Optional[AutoScaleTask] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        bastion: typing.Optional[builtins.bool] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        node_count: typing.Optional[jsii.Number] = None,
        private_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        public_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
        stickiness_cookie_duration: typing.Optional[aws_cdk.core.Duration] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificate_arn: ACM certificate ARN to import.
        :param aurora_serverless: Whether to use aurora serverless. When enabled, the ``databaseInstanceType`` and ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as the default cluster engine instead. Default: false
        :param auto_scale_task: Autoscaling for the ECS Service. Default: - no ecs service autoscaling
        :param backup_retention: database backup retension. Default: - 7 days
        :param bastion: Create a bastion host for debugging or trouble-shooting. Default: false
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_instance_type: Database instance type. Default: r5.large
        :param database_subnets: VPC subnets for database. Default: - VPC isolated subnets
        :param env: The environment variables to pass to the keycloak container.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param node_count: Number of keycloak node in the cluster. Default: 2
        :param private_subnets: VPC private subnets for keycloak service. Default: - VPC private subnets
        :param public_subnets: VPC public subnets for ALB. Default: - VPC public subnets
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        :param stickiness_cookie_duration: The sticky session duration for the keycloak workload with ALB. Default: - one day
        :param vpc: VPC for the workload.
        '''
        props = KeyCloakProps(
            certificate_arn=certificate_arn,
            aurora_serverless=aurora_serverless,
            auto_scale_task=auto_scale_task,
            backup_retention=backup_retention,
            bastion=bastion,
            cluster_engine=cluster_engine,
            database_instance_type=database_instance_type,
            database_subnets=database_subnets,
            env=env,
            instance_engine=instance_engine,
            node_count=node_count,
            private_subnets=private_subnets,
            public_subnets=public_subnets,
            single_db_instance=single_db_instance,
            stickiness_cookie_duration=stickiness_cookie_duration,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDatabase")
    def add_database(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
    ) -> Database:
        '''
        :param vpc: The VPC for the database.
        :param aurora_serverless: enable aurora serverless. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_subnets: VPC subnets for database.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param instance_type: The database instance type. Default: r5.large
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        '''
        props = DatabaseProps(
            vpc=vpc,
            aurora_serverless=aurora_serverless,
            backup_retention=backup_retention,
            cluster_engine=cluster_engine,
            database_subnets=database_subnets,
            instance_engine=instance_engine,
            instance_type=instance_type,
            single_db_instance=single_db_instance,
        )

        return typing.cast(Database, jsii.invoke(self, "addDatabase", [props]))

    @jsii.member(jsii_name="addKeyCloakContainerService")
    def add_key_cloak_container_service(
        self,
        *,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
        database: Database,
        keycloak_secret: aws_cdk.aws_secretsmanager.ISecret,
        vpc: aws_cdk.aws_ec2.IVpc,
        auto_scale_task: typing.Optional[AutoScaleTask] = None,
        bastion: typing.Optional[builtins.bool] = None,
        circuit_breaker: typing.Optional[builtins.bool] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_count: typing.Optional[jsii.Number] = None,
        private_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        public_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        stickiness_cookie_duration: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> ContainerService:
        '''
        :param certificate: The ACM certificate.
        :param database: The RDS database for the service.
        :param keycloak_secret: The secrets manager secret for the keycloak.
        :param vpc: The VPC for the service.
        :param auto_scale_task: Autoscaling for the ECS Service. Default: - no ecs service autoscaling
        :param bastion: Whether to create the bastion host. Default: false
        :param circuit_breaker: Whether to enable the ECS service deployment circuit breaker. Default: false
        :param env: The environment variables to pass to the keycloak container.
        :param node_count: Number of keycloak node in the cluster. Default: 1
        :param private_subnets: VPC subnets for keycloak service.
        :param public_subnets: VPC public subnets for ALB.
        :param stickiness_cookie_duration: The sticky session duration for the keycloak workload with ALB. Default: - one day
        '''
        props = ContainerServiceProps(
            certificate=certificate,
            database=database,
            keycloak_secret=keycloak_secret,
            vpc=vpc,
            auto_scale_task=auto_scale_task,
            bastion=bastion,
            circuit_breaker=circuit_breaker,
            env=env,
            node_count=node_count,
            private_subnets=private_subnets,
            public_subnets=public_subnets,
            stickiness_cookie_duration=stickiness_cookie_duration,
        )

        return typing.cast(ContainerService, jsii.invoke(self, "addKeyCloakContainerService", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="db")
    def db(self) -> typing.Optional[Database]:
        return typing.cast(typing.Optional[Database], jsii.get(self, "db"))


@jsii.data_type(
    jsii_type="cdk-keycloak.KeyCloakProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_arn": "certificateArn",
        "aurora_serverless": "auroraServerless",
        "auto_scale_task": "autoScaleTask",
        "backup_retention": "backupRetention",
        "bastion": "bastion",
        "cluster_engine": "clusterEngine",
        "database_instance_type": "databaseInstanceType",
        "database_subnets": "databaseSubnets",
        "env": "env",
        "instance_engine": "instanceEngine",
        "node_count": "nodeCount",
        "private_subnets": "privateSubnets",
        "public_subnets": "publicSubnets",
        "single_db_instance": "singleDbInstance",
        "stickiness_cookie_duration": "stickinessCookieDuration",
        "vpc": "vpc",
    },
)
class KeyCloakProps:
    def __init__(
        self,
        *,
        certificate_arn: builtins.str,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        auto_scale_task: typing.Optional[AutoScaleTask] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        bastion: typing.Optional[builtins.bool] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        node_count: typing.Optional[jsii.Number] = None,
        private_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        public_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
        stickiness_cookie_duration: typing.Optional[aws_cdk.core.Duration] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param certificate_arn: ACM certificate ARN to import.
        :param aurora_serverless: Whether to use aurora serverless. When enabled, the ``databaseInstanceType`` and ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as the default cluster engine instead. Default: false
        :param auto_scale_task: Autoscaling for the ECS Service. Default: - no ecs service autoscaling
        :param backup_retention: database backup retension. Default: - 7 days
        :param bastion: Create a bastion host for debugging or trouble-shooting. Default: false
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_instance_type: Database instance type. Default: r5.large
        :param database_subnets: VPC subnets for database. Default: - VPC isolated subnets
        :param env: The environment variables to pass to the keycloak container.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param node_count: Number of keycloak node in the cluster. Default: 2
        :param private_subnets: VPC private subnets for keycloak service. Default: - VPC private subnets
        :param public_subnets: VPC public subnets for ALB. Default: - VPC public subnets
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        :param stickiness_cookie_duration: The sticky session duration for the keycloak workload with ALB. Default: - one day
        :param vpc: VPC for the workload.
        '''
        if isinstance(auto_scale_task, dict):
            auto_scale_task = AutoScaleTask(**auto_scale_task)
        if isinstance(database_subnets, dict):
            database_subnets = aws_cdk.aws_ec2.SubnetSelection(**database_subnets)
        if isinstance(private_subnets, dict):
            private_subnets = aws_cdk.aws_ec2.SubnetSelection(**private_subnets)
        if isinstance(public_subnets, dict):
            public_subnets = aws_cdk.aws_ec2.SubnetSelection(**public_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "certificate_arn": certificate_arn,
        }
        if aurora_serverless is not None:
            self._values["aurora_serverless"] = aurora_serverless
        if auto_scale_task is not None:
            self._values["auto_scale_task"] = auto_scale_task
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if bastion is not None:
            self._values["bastion"] = bastion
        if cluster_engine is not None:
            self._values["cluster_engine"] = cluster_engine
        if database_instance_type is not None:
            self._values["database_instance_type"] = database_instance_type
        if database_subnets is not None:
            self._values["database_subnets"] = database_subnets
        if env is not None:
            self._values["env"] = env
        if instance_engine is not None:
            self._values["instance_engine"] = instance_engine
        if node_count is not None:
            self._values["node_count"] = node_count
        if private_subnets is not None:
            self._values["private_subnets"] = private_subnets
        if public_subnets is not None:
            self._values["public_subnets"] = public_subnets
        if single_db_instance is not None:
            self._values["single_db_instance"] = single_db_instance
        if stickiness_cookie_duration is not None:
            self._values["stickiness_cookie_duration"] = stickiness_cookie_duration
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def certificate_arn(self) -> builtins.str:
        '''ACM certificate ARN to import.'''
        result = self._values.get("certificate_arn")
        assert result is not None, "Required property 'certificate_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aurora_serverless(self) -> typing.Optional[builtins.bool]:
        '''Whether to use aurora serverless.

        When enabled, the ``databaseInstanceType`` and
        ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as
        the default cluster engine instead.

        :default: false
        '''
        result = self._values.get("aurora_serverless")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_scale_task(self) -> typing.Optional[AutoScaleTask]:
        '''Autoscaling for the ECS Service.

        :default: - no ecs service autoscaling
        '''
        result = self._values.get("auto_scale_task")
        return typing.cast(typing.Optional[AutoScaleTask], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''database backup retension.

        :default: - 7 days
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def bastion(self) -> typing.Optional[builtins.bool]:
        '''Create a bastion host for debugging or trouble-shooting.

        :default: false
        '''
        result = self._values.get("bastion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster_engine(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''The database cluster engine.

        :default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        '''
        result = self._values.get("cluster_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def database_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Database instance type.

        :default: r5.large
        '''
        result = self._values.get("database_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def database_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnets for database.

        :default: - VPC isolated subnets
        '''
        result = self._values.get("database_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The environment variables to pass to the keycloak container.'''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_engine(self) -> typing.Optional[aws_cdk.aws_rds.IInstanceEngine]:
        '''The database instance engine.

        :default: - MySQL 8.0.21
        '''
        result = self._values.get("instance_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IInstanceEngine], result)

    @builtins.property
    def node_count(self) -> typing.Optional[jsii.Number]:
        '''Number of keycloak node in the cluster.

        :default: 2
        '''
        result = self._values.get("node_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def private_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC private subnets for keycloak service.

        :default: - VPC private subnets
        '''
        result = self._values.get("private_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def public_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC public subnets for ALB.

        :default: - VPC public subnets
        '''
        result = self._values.get("public_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def single_db_instance(self) -> typing.Optional[builtins.bool]:
        '''Whether to use single RDS instance rather than RDS cluster.

        Not recommended for production.

        :default: false
        '''
        result = self._values.get("single_db_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stickiness_cookie_duration(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The sticky session duration for the keycloak workload with ALB.

        :default: - one day
        '''
        result = self._values.get("stickiness_cookie_duration")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC for the workload.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KeyCloakProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AutoScaleTask",
    "ContainerService",
    "ContainerServiceProps",
    "Database",
    "DatabaseCofig",
    "DatabaseProps",
    "KeyCloak",
    "KeyCloakProps",
]

publication.publish()
