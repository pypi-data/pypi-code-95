import os
from typing import List, Optional, Tuple

from openapi_client.models import (
    ProtoVolumeMountRequest,
    ProtoVolumeMountRequests,
    ProtoVolumeMountRequestSourceCLIDrivenProject,
    ProtoVolumeMountRequestSourceDataset,
    ProtoVolumeMountRequestSourceDatasetVersion,
    ProtoVolumeMountRequestSourceProject,
    ProtoVolumeMountRequestSourceVersionControlProject,
    ResponseFileMetadata,
    VolumeFileCopyAPIPayload,
    VolumeFileCreateAPIPayload,
)
from savvihub import vessl_api
from savvihub.organization import _get_organization_name
from savvihub.project import _get_project
from savvihub.util.constant import (
    DATASET_VERSION_HASH_LATEST,
    MOUNT_PATH_EMPTY_DIR,
    MOUNT_PATH_PROJECT,
    MOUNT_TYPE_DATASET,
    MOUNT_TYPE_DATSET_VERSION,
    MOUNT_TYPE_EMPTY_DIR,
    MOUNT_TYPE_OUTPUT,
    MOUNT_TYPE_PROJECT,
    PROJECT_TYPE_CLI_DRIVEN,
    PROJECT_TYPE_VERSION_CONTROL,
)
from savvihub.util.downloader import Downloader
from savvihub.util.exception import InvalidVolumeFileError, SavvihubApiException
from savvihub.util.git import get_git_branch, get_git_diff_path, get_git_ref
from savvihub.util.uploader import Uploader
from savvihub.util.zipper import Zipper


def read_volume_file(volume_id: int, path: str) -> ResponseFileMetadata:
    return vessl_api.volume_file_read_api(volume_id=volume_id, path=path)


def list_volume_files(
    volume_id: int,
    need_download_url: bool = False,
    path: str = "",
    recursive: bool = False,
) -> List[ResponseFileMetadata]:
    return vessl_api.volume_file_list_api(
        volume_id=volume_id,
        recursive=recursive,
        path=path,
        need_download_url=need_download_url,
    ).results


def create_volume_file(volume_id: int, is_dir: bool, path: str) -> ResponseFileMetadata:
    return vessl_api.volume_file_create_api(
        volume_id=volume_id,
        volume_file_create_api_payload=VolumeFileCreateAPIPayload(
            is_dir=is_dir,
            path=path,
        ),
    )


def delete_volume_file(
    volume_id: int, path: str, recursive: bool = False
) -> List[ResponseFileMetadata]:
    return vessl_api.volume_file_delete_api(
        volume_id=volume_id, path=path, recursive=recursive
    ).deleted_files


def upload_volume_file(volume_id: int, path: str) -> ResponseFileMetadata:
    return vessl_api.volume_file_uploaded_api(volume_id=volume_id, path=path)


def copy_volume_file(
    source_volume_id: Optional[int],
    source_path: str,
    dest_volume_id: Optional[int],
    dest_path: str,
    recursive: bool = False,
) -> None:
    if source_volume_id is None:
        return _copy_volume_file_local_to_remote(
            source_path, dest_volume_id, dest_path, recursive
        )

    if dest_volume_id is None:
        return _copy_volume_file_remote_to_local(
            source_volume_id, source_path, dest_path, recursive
        )

    return _copy_volume_file_remote_to_remote(
        source_volume_id, source_path, dest_volume_id, dest_path, recursive
    )


def _copy_volume_file_local_to_remote(
    source_path: str, dest_volume_id: int, dest_path: str, recursive: bool
) -> None:
    """Copy local to remote

    Behavior works like linux cp command
    - `source_path` is file
      - `dest_path` is not a directory: copy as file with new name
      - `dest_path` is directory: copy file into directory with original name
    - `source_path` is directory
      - `dest_path` is file: error
      - `dest_path` does not exist: create `dest_path` and copy contents of `source_path`
      - `dest_path` exists: copy `source_path` as subdirectory of `dest_path`
    """

    output = "Successfully uploaded {} out of {} file(s)."
    source_path = source_path.rstrip("/")

    try:
        dest_file = read_volume_file(dest_volume_id, dest_path)
    except SavvihubApiException:
        dest_file = None

    if not os.path.isdir(source_path):
        if dest_file and (dest_file.is_dir or dest_path.endswith("/")):
            dest_path = os.path.join(dest_path, os.path.basename(source_path))

        uploaded_file = Uploader.upload(source_path, dest_volume_id, dest_path)

        print(output.format(1, 1))
        return uploaded_file

    if dest_file and not dest_file.is_dir:
        raise InvalidVolumeFileError(
            f"Destination path is not a directory: {dest_path}."
        )

    if dest_file and dest_file.is_dir:
        dest_path = os.path.join(dest_path, os.path.basename(source_path))

    paths = Uploader.get_paths_in_dir(source_path)
    uploaded_files = Uploader.bulk_upload(source_path, paths, dest_volume_id, dest_path)

    print(output.format(len(uploaded_files), len(paths)))
    return uploaded_files


def _copy_volume_file_remote_to_local(
    source_volume_id: int, source_path: str, dest_path: str, recursive: bool
) -> None:
    """Copy remote to local

    Behavior works like linux cp command
    - `source_path` is file
      - `dest_path` is not a directory: copy as file with new name
      - `dest_path` is directory: copy file into directory with original name
    - `source_path` is directory
      - `dest_path` is file: error
      - `dest_path` does not exist: create `dest_path` and copy contents of `source_path`
      - `dest_path` exists: copy `source_path` as subdirectory of `dest_path`
    """

    output = "Successfully downloaded {} out of {} file(s)."
    source_file = read_volume_file(source_volume_id, source_path)

    if not source_file.is_dir:
        if os.path.isdir(dest_path):
            dest_path = os.path.join(dest_path, os.path.basename(source_file.path))

        Downloader.download(dest_path, source_file)

        print(output.format(1, 1))
        return

    files = list_volume_files(
        volume_id=source_volume_id,
        need_download_url=True,
        path=source_path,
        recursive=True,
    )

    if os.path.isfile(dest_path):
        raise InvalidVolumeFileError(
            f"Destination path is not a directory: {dest_path}."
        )

    prefix = source_path.rstrip("/")
    if os.path.isdir(dest_path):
        prefix = os.path.dirname(prefix)

    if prefix:
        prefix += "/"
        for file in files:
            file.path = file.path.replace(prefix, "", 1)

    downloaded_files = Downloader.bulk_download(dest_path, files)
    print(output.format(len(downloaded_files), len([x for x in files if not x.is_dir])))


def _copy_volume_file_remote_to_remote(
    source_volume_id: int,
    source_path: str,
    dest_volume_id: int,
    dest_path: str,
    recursive: bool,
) -> None:
    if source_volume_id != dest_volume_id:
        raise InvalidVolumeFileError("Files can only be copied within the same volume.")

    files = vessl_api.volume_file_copy_api(
        volume_id=source_volume_id,
        volume_file_copy_api_payload=VolumeFileCopyAPIPayload(
            dest_path=dest_path,
            recursive=recursive,
            source_dataset_version="latest",
            source_path=source_path,
        ),
    ).copied_files

    print(f"Successfully downloaded {len(files)} out of {len(files)} file(s).")


def _configure_volume_mount_requests(
    dataset_mounts: List[Tuple[str, str]],
    root_volume_size: str,
    working_dir: str,
    output_dir: str,
    local_project_url: str,
    **kwargs,
) -> ProtoVolumeMountRequests:
    requests = [
        _configure_volume_mount_request_empty_dir(),
        _configure_volume_mount_request_output(output_dir),
        _configure_volume_mount_request_project(local_project_url, **kwargs),
    ]

    if dataset_mounts is not None:
        requests += [
            _configure_volume_mount_request_dataset(mount_path, dataset_name, **kwargs)
            for mount_path, dataset_name in dataset_mounts
        ]

    return ProtoVolumeMountRequests(
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        requests=requests,
    )


def _configure_volume_mount_request_dataset(
    mount_path: str, dataset_name: str, **kwargs
) -> ProtoVolumeMountRequest:
    from savvihub.dataset import read_dataset, read_dataset_version

    mount_path = os.path.join(mount_path, "")  # Ensure path ends in /

    organization_name = _get_organization_name(**kwargs)
    dataset_version_hash = DATASET_VERSION_HASH_LATEST

    if "@" in dataset_name:
        # Example: mnist@3d1e0f91c
        dataset_name, dataset_version_hash = dataset_name.split("@", 1)

    if "/" in dataset_name:
        # Example: org1/mnist@3d1e0f91c
        organization_name, dataset_name = dataset_name.split("/", 1)

    dataset = read_dataset(dataset_name, organization_name=organization_name)

    if not dataset.is_version_enabled:
        return ProtoVolumeMountRequest(
            mount_type=MOUNT_TYPE_DATASET,
            mount_path=mount_path,
            dataset=ProtoVolumeMountRequestSourceDataset(
                dataset_id=dataset.id,
                dataset_name=dataset_name,
            ),
        )

    if dataset_version_hash != DATASET_VERSION_HASH_LATEST:
        dataset_version_hash = read_dataset_version(
            dataset.id, dataset_version_hash
        ).version_hash  # Get full version hash

    return ProtoVolumeMountRequest(
        mount_type=MOUNT_TYPE_DATSET_VERSION,
        mount_path=mount_path,
        dataset_version=ProtoVolumeMountRequestSourceDatasetVersion(
            dataset_id=dataset.id,
            dataset_name=dataset_name,
            dataset_version_hash=dataset_version_hash,
        ),
    )


def _configure_volume_mount_request_empty_dir() -> ProtoVolumeMountRequest:
    return ProtoVolumeMountRequest(
        mount_type=MOUNT_TYPE_EMPTY_DIR,
        mount_path=MOUNT_PATH_EMPTY_DIR,
    )


def _configure_volume_mount_request_output(output_dir: str) -> ProtoVolumeMountRequest:
    return ProtoVolumeMountRequest(
        mount_type=MOUNT_TYPE_OUTPUT,
        mount_path=output_dir,
    )


def _configure_volume_mount_request_project(
    local_project_url: str,
    **kwargs,
) -> ProtoVolumeMountRequest:
    project = _get_project(**kwargs)

    volume_mount_project = ProtoVolumeMountRequestSourceProject(
        project_id=project.id,
        project_type=project.type,
    )

    if project.type == PROJECT_TYPE_VERSION_CONTROL:
        volume_mount_project.version_control_project = (
            ProtoVolumeMountRequestSourceVersionControlProject(
                project_branch=get_git_branch(project, **kwargs),
                project_git_ref=get_git_ref(project, **kwargs),
                project_git_diff=get_git_diff_path(project, **kwargs),
            )
        )

    elif project.type == PROJECT_TYPE_CLI_DRIVEN:
        if local_project_url is None:
            # Create zip file in the parent of the current working directory

            cwd = os.path.abspath(os.getcwd())
            zip_path = os.path.abspath(
                os.path.join(os.path.join(cwd, os.pardir), f"{project.name}.zip")
            )
            zipper = Zipper(zip_path, "w")
            zipper.zipdir(cwd, zipper)
            zipper.close()

            uploaded = Uploader.upload(
                local_path=zipper.filename,
                volume_id=project.volume_id,
                remote_path=os.path.basename(zipper.filename),
            )
            local_project_url = uploaded.path

            os.remove(zipper.filename)

        volume_mount_project.cli_driven_project = (
            ProtoVolumeMountRequestSourceCLIDrivenProject(
                local_project=local_project_url,
            )
        )

    return ProtoVolumeMountRequest(
        mount_type=MOUNT_TYPE_PROJECT,
        mount_path=MOUNT_PATH_PROJECT.format(project.name),
        project=volume_mount_project,
    )
