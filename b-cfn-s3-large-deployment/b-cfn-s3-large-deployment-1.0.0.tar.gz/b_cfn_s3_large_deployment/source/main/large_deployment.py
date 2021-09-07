import json
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Any, Dict, Optional
from uuid import uuid4
from zipfile import ZipFile

logger = logging.getLogger()


@dataclass
class LargeDeployment:
    mount_path: str
    source_bucket_names: List[str]
    source_object_keys: List[str]
    destination_bucket_name: str
    destination_bucket_key_prefix: str
    old_destination_bucket_name: str
    old_destination_bucket_key_prefix: str
    retain_on_delete: bool
    user_metadata: Dict[str, Any]
    system_metadata: Dict[str, Any]
    prune: bool
    exclude: List[str]
    include: List[str]

    def __post_init__(self):
        self.destination_bucket_key_prefix = self.__format_bucket_key_prefix(self.destination_bucket_key_prefix)
        self.old_destination_bucket_key_prefix = self.__format_bucket_key_prefix(self.old_destination_bucket_key_prefix)

    @property
    def s3_source_objects_uris(self) -> List[str]:
        return [f's3://{name}/{key}' for name, key in zip(self.source_bucket_names, self.source_object_keys)]

    @property
    def s3_destination_uri(self) -> str:
        return f's3://{self.destination_bucket_name}/{self.destination_bucket_key_prefix}'

    @property
    def old_s3_destination_uri(self) -> Optional[str]:
        return (
            f's3://{self.old_destination_bucket_name}/{self.old_destination_bucket_key_prefix}'
            if self.old_destination_bucket_name or self.old_destination_bucket_key_prefix
            else None
        )

    def s3_deploy(self) -> None:
        # Create a temporary working directory in /tmp or if enabled an attached efs volume.
        if self.mount_path is None:
            workdir_path = tempfile.mkdtemp()
        else:
            workdir_path = os.path.join(self.mount_path, str(uuid4()))
            os.mkdir(workdir_path)

        logger.info(f'workdir path: {workdir_path}')

        # Create a directory into which we extract the contents of the zip file.
        contents_dirpath = os.path.join(workdir_path, 'contents')
        os.mkdir(contents_dirpath)

        try:
            # Download the archive from the source and extract to "contents".
            for s3_source_uri in self.s3_source_objects_uris:
                archive_path = os.path.join(workdir_path, str(uuid4()))
                logger.info(f'archive path: {archive_path}')
                aws_command('s3', 'cp', s3_source_uri, archive_path)
                logger.info(f'extracting archive to: {contents_dirpath}\n')
                with ZipFile(archive_path, 'r') as zip_file:
                    zip_file.extractall(contents_dirpath)

            # Sync from "contents" to destination.

            s3_sync_command = ['s3', 'sync']

            if self.prune:
                s3_sync_command.append('--delete')

            if self.exclude:
                for filter_ in self.exclude:
                    s3_sync_command.extend(['--exclude', filter_])

            if self.include:
                for filter_ in self.include:
                    s3_sync_command.extend(['--include', filter_])

            s3_sync_command.extend([contents_dirpath, self.s3_destination_uri, *self.__create_metadata_args()])
            aws_command(*s3_sync_command)
        finally:
            shutil.rmtree(workdir_path)

    def __create_metadata_args(self) -> List[str]:
        if len(self.user_metadata) == 0 and len(self.system_metadata) == 0:
            return []

        system_metadata = {k.lower(): v for k, v in self.system_metadata.items()}
        user_metadata = {k.lower(): v for k, v in self.user_metadata.items()}

        flatten = lambda l: [item for sublist in l for item in sublist]
        system_args = flatten([[f'--{k}', v] for k, v in system_metadata.items()])
        user_args = ['--metadata', json.dumps(user_metadata, separators=(',', ':'))] if len(user_metadata) > 0 else []

        return system_args + user_args + ['--metadata-directive', 'REPLACE']

    @staticmethod
    def __format_bucket_key_prefix(prefix: str) -> str:
        return os.path.join('/', prefix)[1:]


def aws_command(*args) -> None:
    # From ``AwsCliLayer``.
    aws = '/opt/awscli/aws'
    logger.info(f'aws {" ".join(args)}')
    subprocess.check_call([aws] + list(args))
