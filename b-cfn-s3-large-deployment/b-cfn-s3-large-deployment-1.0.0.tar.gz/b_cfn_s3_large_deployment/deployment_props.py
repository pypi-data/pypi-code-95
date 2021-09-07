from dataclasses import dataclass
from typing import List

from aws_cdk.aws_ec2 import IVpc, SubnetSelection
from aws_cdk.aws_iam import IRole
from aws_cdk.aws_s3 import IBucket, StorageClass
from aws_cdk.core import Expiration

from b_cfn_s3_large_deployment.deployment_source import BaseDeploymentSource
from b_cfn_s3_large_deployment.efs_props import EfsProps


@dataclass
class DeploymentProps:
    """
    Large deployment properties.

    Properties
    ----------

    ``source``
        The sources from which to deploy the contents of this bucket.

    ``destination_bucket``
        The S3 bucket to sync the contents of the zip file to.

    ``destination_key_prefix``
        Key prefix in the destination bucket. By default unzip to root of
        the destination bucket.

    ``exclude``
        If this is set, matching files or objects will be excluded from the deployment's sync
        command. This can be used to exclude a file from being pruned in the destination bucket.

        If you want to just exclude files from the deployment package (which excludes these files
        evaluated when invalidating the asset), you should leverage the ``exclude`` property of
        ``AssetOptions`` when defining your source.

        By default no exclude filters are used.

        More info: https://docs.aws.amazon.com/cli/latest/reference/s3/index.html#use-of-exclude-and-include-filters

    ``include``
        If this is set, matching files or objects will be included with the deployment's sync
        command. Since all files from the deployment package are included by default, this property
        is usually leveraged alongside an `exclude` filter.

        By default no include filters are used and all files are included with the sync command.

        More info: https://docs.aws.amazon.com/cli/latest/reference/s3/index.html#use-of-exclude-and-include-filters

    ``prune``
        If this is set to false, files in the destination bucket that
        do not exist in the asset, will NOT be deleted during deployment (create/update).

        Default is true.

        https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html

    ``retain_on_delete``
        If this is set to "false", the destination files will be deleted when the
        resource is deleted or the destination is updated.

        Default is true - when resource is deleted/updated, files are retained.

        NOTE: Configuring this to "false" might have operational implications. Please
        visit to the package documentation referred below to make sure you fully understand those implications.

        https://github.com/aws/aws-cdk/tree/master/packages/%40aws-cdk/aws-s3-deployment#retain-on-delete

    ``memory_limit``
        The amount of memory (in MiB) to allocate to the AWS Lambda function which
        replicates the files from the CDK bucket to the destination bucket.

        If you are deploying large files, you will need to increase this number
        accordingly.

        Default is 256.

    ``use_efs``
        Mount an EFS file system. Enable this if your assets are large and you encounter disk space errors.

        By default EFS is not used. Lambda has access only to 512MB of disk space.

    ``efs_props``
        Custom EFS properties. If not set, default properties are used.

    ``role``
        Execution role associated with this function.

        By default role is automatically created.

    ``content_encoding``
        System-defined content-encoding metadata to be set on all objects in the deployment.

        By default content encoding is not set.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#SysMetadata

    ``content_language``
        System-defined content-language metadata to be set on all objects in the deployment.

        By default content language is not set.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#SysMetadata

    ``content_type``
        System-defined content-type metadata to be set on all objects in the deployment.

        By default content type is not set.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#SysMetadata

    ``expires``
        System-defined expires metadata to be set on all objects in the deployment.

        By default the objects in the distribution will not expire.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#SysMetadata

    ``storage_class``
        System-defined x-amz-storage-class metadata to be set on all objects in the deployment.

        If not set, the default storage-class for the bucket is used.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#SysMetadata

    ``vpc``
        The VPC network to place the deployment lambda handler in. This is required if `useEfs` is set.

        Default is ``None``.

    ``vpc_subnets``
        Where in the VPC to place the deployment lambda handler. Only used if 'vpc' is supplied.

        By default the Vpc default strategy is used if not specified otherwise.
    """

    sources: List[BaseDeploymentSource]
    destination_bucket: IBucket
    destination_key_prefix: str = None
    exclude: List[str] = None
    include: List[str] = None
    prune: bool = True
    retain_on_delete: bool = True
    memory_limit: int = 256
    use_efs: bool = False
    efs_props: EfsProps = None
    role: IRole = None
    content_encoding: str = None
    content_language: str = None
    content_type: str = None
    expires: Expiration = None
    storage_class: StorageClass = None
    vpc: IVpc = None
    vpc_subnets: SubnetSelection = None
