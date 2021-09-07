from abc import ABC, abstractmethod
from dataclasses import dataclass

from aws_cdk.aws_iam import IRole
from aws_cdk.aws_s3 import IBucket
from aws_cdk.aws_s3_assets import AssetOptions, Asset
from aws_cdk.core import Construct


@dataclass
class DeploymentSourceConfig:
    """
    Bound deployment source configuration.

    Initialized by ``BaseDeploymentSource.bind()`` method.
    """

    bucket: IBucket
    zip_object_key: str


@dataclass
class DeploymentSourceContext:
    """
    Deployment source context.
    """

    handler_role: IRole


class BaseDeploymentSource(ABC):
    @abstractmethod
    def bind(self, scope: Construct, context: DeploymentSourceContext) -> DeploymentSourceConfig:
        """
        Bind deployment source to the given scope.

        :param scope: AWS CDK scope (stack or other valid construct).
        :param context: Additional necessary contextual data.

        :return: Bound source configuration.
        """
        pass


class BucketDeploymentSource(BaseDeploymentSource):
    """
    Uses a .zip file stored in an S3 bucket as the source for the destination bucket contents.

    Make sure you trust the producer of the archive.

    :param bucket: The S3 Bucket.
    :param zip_object_key: The S3 object key of the zip file with contents.
    """

    def __init__(self, bucket: IBucket, zip_object_key: str):
        self.__bucket = bucket
        self.__zip_object_key = zip_object_key

    def bind(self, scope: Construct, context: DeploymentSourceContext) -> DeploymentSourceConfig:
        if not context:
            raise ValueError('To use a ``BucketDeploymentSource``, context must be provided.')

        self.__bucket.grant_read(context.handler_role)

        return DeploymentSourceConfig(self.__bucket, self.__zip_object_key)


class AssetDeploymentSource(BaseDeploymentSource):
    """
    Uses a local asset as the deployment source.

    If the local asset is a .zip archive, make sure you trust the
    producer of the archive.

    :param path: The path to a local .zip file or a directory.
    :param options: Optional asset options.
    """

    def __init__(self, path: str, options: AssetOptions = None):
        self.__path = path
        self.__options = options or AssetOptions()

    def bind(self, scope: Construct, context: DeploymentSourceContext) -> DeploymentSourceConfig:
        if not context:
            raise ValueError('To use a ``AssetDeploymentSource``, context must be provided.')

        id_ = 1
        while scope.node.try_find_child(f'Asset{id_}'):
            id_ += 1

        asset = Asset(
            scope,
            f'Asset{id_}',
            path=self.__path,
            readers=self.__options.readers,
            source_hash=self.__options.source_hash,
            exclude=self.__options.exclude,
            follow=self.__options.follow,
            ignore_mode=self.__options.ignore_mode,
            follow_symlinks=self.__options.follow_symlinks,
            asset_hash=self.__options.asset_hash,
            asset_hash_type=self.__options.asset_hash_type,
            bundling=self.__options.bundling,
        )

        if not asset.is_zip_archive:
            raise ValueError('Asset path must be either a .zip file or a directory.')

        asset.grant_read(context.handler_role)

        return DeploymentSourceConfig(asset.bucket, asset.s3_object_key)
