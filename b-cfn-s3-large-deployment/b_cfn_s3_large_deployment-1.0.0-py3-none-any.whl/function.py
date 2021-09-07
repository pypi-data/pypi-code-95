import os
from functools import lru_cache
from importlib.resources import path

from aws_cdk.aws_efs import IAccessPoint
from aws_cdk.aws_lambda import Code, SingletonFunction, Runtime, FileSystem as LambdaFileSystem
from aws_cdk.core import Stack, Duration
from aws_cdk.lambda_layer_awscli import AwsCliLayer

import b_cfn_s3_large_deployment
from b_cfn_s3_large_deployment.deployment_props import DeploymentProps


class S3LargeDeploymentFunction(SingletonFunction):
    def __init__(
            self,
            scope: Stack,
            name: str,
            deployment_props: DeploymentProps,
            mount_path: str = None,
            access_point: IAccessPoint = None
    ) -> None:
        if deployment_props.use_efs and (mount_path is None or access_point is None):
            raise ValueError('While using EFS its access point and mount path must be set.')

        self.__name = name
        super().__init__(
            scope=scope,
            id=name,
            uuid=f'{name}-uuid',
            function_name=name,
            code=self.__code(),
            timeout=Duration.minutes(15),
            handler='main.index.handler',
            runtime=Runtime.PYTHON_3_7,
            layers=[
                AwsCliLayer(scope, f'{name}AwsCliLayer')
            ],
            environment=None if not deployment_props.use_efs else {
                'MOUNT_PATH': mount_path
            },
            role=deployment_props.role,
            memory_size=deployment_props.memory_limit,
            vpc=deployment_props.vpc,
            vpc_subnets=deployment_props.vpc_subnets,
            filesystem=(
                LambdaFileSystem.from_efs_access_point(access_point, mount_path)
                if deployment_props.use_efs
                else None
            )
        )

        if access_point:
            self.node.add_dependency(access_point)

        deployment_props.destination_bucket.grant_read_write(self)

    @lru_cache
    def __code(self) -> Code:
        with path(b_cfn_s3_large_deployment, 'source') as source_path:
            return Code.from_asset(os.path.join(source_path))

    @property
    def function_name(self):
        return self.__name
