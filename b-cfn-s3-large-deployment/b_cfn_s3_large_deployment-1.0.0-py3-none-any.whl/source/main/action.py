import json
import logging
import os
from typing import Any, Dict, Optional, NamedTuple
from uuid import uuid4

from .large_deployment import LargeDeployment, aws_command

logger = logging.getLogger()

ENV_KEY_MOUNT_PATH = 'MOUNT_PATH'


class ActionResult(NamedTuple):
    """
    Custom data to return back to CloudFormation service and
    physical resource id (can be empty).
    """

    data: Optional[Dict[Any, Any]]
    resource_id: str = None


class Action:
    def __init__(self, invocation_event: Dict[str, Any]):
        self.__invocation_event: Dict[str, Any] = invocation_event
        self.__properties: Dict[str, Any] = invocation_event['ResourceProperties']
        self.__old_properties = invocation_event.get('OldResourceProperties', {})
        self.__resource_id: Optional[str] = invocation_event.get('PhysicalResourceId')
        self.__deployment = self.__parse_properties(mount_path=os.getenv(ENV_KEY_MOUNT_PATH))

    def create(self) -> ActionResult:
        """
        Creates a resource.

        :return: A tuple containing two items:
            1. Custom data to return back to CloudFormation service.
            2. Physical resource id (can be empty).
        """

        logger.info(f'Initiating resource creation with these properties: {json.dumps(self.__properties)}.')

        logger.info(f's3_source_objects_uris={self.__deployment.s3_source_objects_uris}')
        logger.info(f's3_destination_uri={self.__deployment.s3_destination_uri}')
        logger.info(f'old_s3_destination_uri={self.__deployment.old_s3_destination_uri}')

        self.__deployment.s3_deploy()

        return ActionResult(None, resource_id=f'custom-s3-large-deployment-{str(uuid4())}')

    def update(self) -> ActionResult:
        """
        Updates a resource.

        :return: A tuple containing two items:
            1. Custom data to return back to CloudFormation service.
            2. Physical resource id (can be empty).
        """

        logger.info(f'Initiating resource update with these parameters: {json.dumps(self.__properties)}.')

        if not self.__resource_id:
            raise ValueError(f'Resource id is not defined.')

        logger.info(f's3_source_objects_uris={self.__deployment.s3_source_objects_uris}')
        logger.info(f's3_destination_uri={self.__deployment.s3_destination_uri}')
        logger.info(f'old_s3_destination_uri={self.__deployment.old_s3_destination_uri}')

        if (
                not self.__deployment.retain_on_delete and
                self.__deployment.old_s3_destination_uri and
                self.__deployment.old_s3_destination_uri != self.__deployment.s3_destination_uri
        ):
            aws_command('s3', 'rm', self.__deployment.old_s3_destination_uri, '--recursive')

        self.__deployment.s3_deploy()

        return ActionResult(None, resource_id=self.__resource_id)

    def delete(self) -> ActionResult:
        """
        Deletes a resource.

        :return: A tuple containing two items:
            1. Custom data to return back to CloudFormation service.
            2. Physical resource id (can be empty).
        """

        logger.info(f'Initiating resource deletion with these parameters: {json.dumps(self.__properties)}.')

        logger.info(f's3_destination_uri={self.__deployment.s3_destination_uri}')

        if not self.__resource_id:
            raise ValueError(f'Resource id is not defined.')

        if not self.__deployment.retain_on_delete:
            aws_command('s3', 'rm', self.__deployment.s3_destination_uri, '--recursive')

        return ActionResult(None, resource_id=self.__resource_id)

    def __parse_properties(self, mount_path: Optional[str]) -> LargeDeployment:
        try:
            return LargeDeployment(
                mount_path=mount_path,
                source_bucket_names=self.__properties['SourceBucketNames'],
                source_object_keys=self.__properties['SourceObjectKeys'],
                destination_bucket_name=self.__properties['DestinationBucketName'],
                destination_bucket_key_prefix=self.__properties.get('DestinationBucketKeyPrefix', ''),
                old_destination_bucket_name=self.__old_properties.get('DestinationBucketName', ''),
                old_destination_bucket_key_prefix=self.__old_properties.get('DestinationBucketKeyPrefix', ''),
                retain_on_delete=self.__properties.get('RetainOnDelete', True),
                user_metadata=self.__properties.get('UserMetadata', {}),
                system_metadata=self.__properties.get('SystemMetadata', {}),
                prune=self.__properties.get('Prune', True),
                exclude=self.__properties.get('Exclude', []),
                include=self.__properties.get('Include', [])
            )
        except KeyError:
            raise
