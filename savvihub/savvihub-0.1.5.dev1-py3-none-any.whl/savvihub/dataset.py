from typing import List

from openapi_client import SavviHubDatasetCreateAPIPayload
from openapi_client.models import (
    GSDatasetCreateAPIPayload,
    ResponseDatasetInfo,
    ResponseDatasetInfoDetail,
    ResponseDatasetVersionInfo,
    ResponseFileMetadata,
    S3DatasetCreateAPIPayload,
)
from savvihub import vessl_api
from savvihub.organization import _get_organization_name
from savvihub.util.constant import DATASET_PATH_SCHEME_GS, DATASET_PATH_SCHEME_S3
from savvihub.util.exception import InvalidDatasetError
from savvihub.volume import copy_volume_file, delete_volume_file, list_volume_files


def read_dataset(dataset_name: str, **kwargs) -> ResponseDatasetInfoDetail:
    """Read dataset

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.dataset_read_api(
        dataset_name=dataset_name, organization_name=_get_organization_name(**kwargs)
    )


def read_dataset_version(
    dataset_id: int, dataset_version_hash: str
) -> ResponseDatasetVersionInfo:
    return vessl_api.dataset_version_read_api(
        dataset_id=dataset_id,
        dataset_version_hash=dataset_version_hash,
    )


def list_datasets(**kwargs) -> List[ResponseDatasetInfo]:
    """List datasets

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.dataset_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results


def _create_dataset_local(
    dataset_name: str,
    is_version_enabled: bool = False,
    description: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    return vessl_api.savvi_hub_dataset_create_api(
        organization_name=_get_organization_name(**kwargs),
        savvi_hub_dataset_create_api_payload=SavviHubDatasetCreateAPIPayload(
            name=dataset_name,
            description=description,
            is_version_enabled=is_version_enabled,
        ),
    )


def _create_dataset_s3(
    dataset_name: str,
    is_version_enabled: bool = False,
    description: str = None,
    external_path: str = None,
    aws_role_arn: str = None,
    version_path: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    if is_version_enabled and (
        version_path is None or not version_path.startswith(DATASET_PATH_SCHEME_S3)
    ):
        raise InvalidDatasetError(f"Invalid version path: {version_path}")

    return vessl_api.s3_dataset_create_api(
        organization_name=_get_organization_name(**kwargs),
        s3_dataset_create_api_payload=S3DatasetCreateAPIPayload(
            name=dataset_name,
            description=description,
            is_version_enabled=is_version_enabled,
            s3_path=external_path,
            version_s3_path=version_path,
            is_public=False,
            aws_role_arn=aws_role_arn,
        ),
    )


def _create_dataset_gs(
    dataset_name: str,
    is_version_enabled: bool = False,
    description: str = None,
    external_path: str = None,
    version_path: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    if is_version_enabled:
        raise InvalidDatasetError("Versioning is not supported for GoogleStorage")

    return vessl_api.g_s_dataset_create_api(
        organization_name=_get_organization_name(**kwargs),
        gs_dataset_create_api_payload=GSDatasetCreateAPIPayload(
            name=dataset_name,
            description=description,
            is_version_enabled=is_version_enabled,
            gs_path=external_path,
            version_gs_path=version_path,
            is_public=False,
        ),
    )


def create_dataset(
    dataset_name: str,
    description: str = None,
    is_version_enabled: bool = False,
    external_path: str = None,
    aws_role_arn: str = None,
    version_path: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    """Create dataset

    Keyword args:
        organization_name (str): override default organization
    """
    if external_path is None:
        return _create_dataset_local(
            dataset_name, is_version_enabled, description, **kwargs
        )

    if external_path.startswith(DATASET_PATH_SCHEME_S3):
        return _create_dataset_s3(
            dataset_name,
            is_version_enabled,
            description,
            external_path,
            aws_role_arn,
            version_path,
            **kwargs,
        )

    if external_path.startswith(DATASET_PATH_SCHEME_GS):
        return _create_dataset_gs(
            dataset_name,
            is_version_enabled,
            description,
            external_path,
            version_path,
            **kwargs,
        )

    raise InvalidDatasetError("Invalid path scheme. Must be either s3:// or gs://.")


def list_dataset_volume_files(
    dataset_name: str,
    need_download_url: bool = False,
    path: str = "",
    recursive: bool = False,
    **kwargs,
) -> List[ResponseFileMetadata]:
    """List dataset volume files

    Keyword args:
        organization_name (str): override default organization
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return list_volume_files(dataset.volume_id, need_download_url, path, recursive)


def upload_dataset_volume_file(
    dataset_name: str,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Upload file to dataset

    Keyword args:
        organization_name (str): override default organization
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return copy_volume_file(
        source_volume_id=None,
        source_path=source_path,
        dest_volume_id=dataset.volume_id,
        dest_path=dest_path,
    )


def download_dataset_volume_file(
    dataset_name: str,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Download file from dataset

    Keyword args:
        organization_name (str): override default organization
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return copy_volume_file(
        source_volume_id=dataset.volume_id,
        source_path=source_path,
        dest_volume_id=None,
        dest_path=dest_path,
    )


def copy_dataset_volume_file(
    dataset_name: str,
    source_path: str,
    dest_path: str,
    recursive: bool = False,
    **kwargs,
) -> None:
    """Copy files within a same dataset

    Keyword args:
        organization_name (str): override default organization
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return copy_volume_file(
        source_volume_id=dataset.volume_id,
        source_path=source_path,
        dest_volume_id=dataset.volume_id,
        dest_path=dest_path,
        recursive=recursive,
    )


def delete_dataset_volume_file(
    dataset_name: str,
    path: str,
    recursive: bool = False,
    **kwargs,
) -> List[ResponseFileMetadata]:
    """Delete dataset volume file

    Keyword args:
        organization_name (str): override default organization
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return delete_volume_file(dataset.volume_id, path, recursive)
