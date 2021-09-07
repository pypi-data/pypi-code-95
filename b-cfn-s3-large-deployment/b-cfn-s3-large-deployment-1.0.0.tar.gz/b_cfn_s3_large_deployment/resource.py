from aws_cdk.aws_ec2 import IVpc
from aws_cdk.aws_efs import FileSystemProps, FileSystem, Acl, PosixUser
from aws_cdk.core import Stack, CustomResource, RemovalPolicy, Construct

from b_cfn_s3_large_deployment.deployment_props import DeploymentProps
from b_cfn_s3_large_deployment.deployment_source import DeploymentSourceContext
from b_cfn_s3_large_deployment.efs_props import EfsProps
from b_cfn_s3_large_deployment.function import S3LargeDeploymentFunction


class S3LargeDeploymentResource(CustomResource):
    """
    Resource that handles S3 assets deployment with large-files support.

    See README file for possible limitations.
    """

    def __init__(
            self,
            scope: Stack,
            name: str,
            props: DeploymentProps
    ):
        if props.use_efs and not props.vpc:
            raise ValueError('Vpc must be specified if ``use_efs`` is set.')

        access_point = None
        access_point_path = '/lambda'
        mount_path = f'/mnt{access_point_path}'
        if props.use_efs and props.vpc:
            file_system = self.__get_efs_filesystem(scope, props.vpc, props.efs_props or EfsProps())
            access_point = file_system.add_access_point(
                f'{name}FunctionAccessPoint',
                path=access_point_path,
                create_acl=Acl(
                    owner_gid='1001',
                    owner_uid='1001',
                    permissions='0777'
                ),
                posix_user=PosixUser(
                    gid='1001',
                    uid='1001'
                )
            )

            access_point.node.add_dependency(file_system.mount_targets_available)

        function = S3LargeDeploymentFunction(
            scope,
            name=f'{name}Function',
            deployment_props=props,
            mount_path=mount_path,
            access_point=access_point
        )

        sources_configs = [
            source.bind(scope, DeploymentSourceContext(handler_role=function.role))
            for source in props.sources
        ]

        super().__init__(
            scope,
            f'CustomResource{name}',
            service_token=function.function_arn,
            removal_policy=RemovalPolicy.DESTROY,
            properties={
                'SourceBucketNames': [src.bucket.bucket_name for src in sources_configs],
                'SourceObjectKeys': [src.zip_object_key for src in sources_configs],
                'DestinationBucketName': props.destination_bucket.bucket_name,
                'DestinationBucketKeyPrefix': props.destination_key_prefix,
                'RetainOnDelete': props.retain_on_delete,
                'Prune': props.prune,
                'Exclude': props.exclude,
                'Include': props.include,
            }
        )

    @staticmethod
    def __get_efs_filesystem(scope: Construct, vpc: IVpc, efs_props: EfsProps) -> FileSystem:
        stack = Stack.of(scope)
        efs_uuid = f'Efs{vpc.node.addr.upper()}'
        file_system_props = FileSystemProps(
            vpc=vpc,
            performance_mode=efs_props.performance_mode,
            provisioned_throughput_per_second=efs_props.provisioned_throughput_per_second,
            removal_policy=efs_props.removal_policy,
            throughput_mode=efs_props.throughput_mode
        )

        return stack.node.try_find_child(efs_uuid) or FileSystem(
            scope,
            id=efs_uuid,
            vpc=file_system_props.vpc,
            enable_automatic_backups=file_system_props.enable_automatic_backups,
            encrypted=file_system_props.encrypted,
            file_system_name=file_system_props.file_system_name,
            kms_key=file_system_props.kms_key,
            lifecycle_policy=file_system_props.lifecycle_policy,
            performance_mode=file_system_props.performance_mode,
            provisioned_throughput_per_second=file_system_props.provisioned_throughput_per_second,
            removal_policy=file_system_props.removal_policy,
            security_group=file_system_props.security_group,
            throughput_mode=file_system_props.throughput_mode,
            vpc_subnets=file_system_props.vpc_subnets
        )
