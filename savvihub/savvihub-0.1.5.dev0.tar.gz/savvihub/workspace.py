import os
import urllib
from pathlib import Path
from typing import List
from zipfile import ZipFile

import paramiko

from openapi_client.models import ResponseWorkspaceDetail, ResponseWorkspaceList
from savvihub import vessl_api
from savvihub.organization import _get_organization_name
from savvihub.util.config import VesslConfigLoader
from savvihub.util.constant import (
    SSH_CONFIG_FORMAT,
    SSH_CONFIG_PATH,
    WORKSPACE_TEMP_ZIP_PATH,
    WORKSPACE_ZIP_PATH,
)
from savvihub.util.exception import InvalidWorkspaceError
from savvihub.util.zipper import Zipper
from savvihub.volume import copy_volume_file


def read_workspace(workspace_id: int, **kwargs) -> ResponseWorkspaceDetail:
    """Read workspace

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.workspace_read_api(
        workspace_id=workspace_id, organization_name=_get_organization_name(**kwargs)
    )


def list_workspaces(
    cluster_id: int = None, statuses: List[str] = None, mine: bool = True, **kwargs
) -> List[ResponseWorkspaceList]:
    """List workspaces

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.workspace_list_api(
        organization_name=_get_organization_name(**kwargs),
        cluster=cluster_id,
        mine=mine,
        statuses=statuses,
    ).results


def backup_workspace() -> None:
    """Backup the home directory of the workspace

    Should only be called inside a workspace.
    """

    workspace_id = VesslConfigLoader().workspace
    if workspace_id is None:
        raise InvalidWorkspaceError("Can only be called within a workspace.")

    workspace = read_workspace(workspace_id)

    zipper = Zipper(WORKSPACE_TEMP_ZIP_PATH, "w")
    zipper.zipdir(str(Path.home()), zipper)
    zipper.close()

    copy_volume_file(
        source_volume_id=None,
        source_path=zipper.filename,
        dest_volume_id=workspace.backup_volume_id,
        dest_path=os.path.basename(zipper.filename),
    )


def restore_workspace() -> None:
    """Restore the home directory from the previous backup

    Should only be called inside a workspace.
    """

    workspace_id = VesslConfigLoader().workspace
    if workspace_id is None:
        raise InvalidWorkspaceError("Can only be called within a workspace.")

    workspace = read_workspace(workspace_id)
    if workspace.last_backup_dt is None:
        raise InvalidWorkspaceError("Backup not found.")

    copy_volume_file(
        source_volume_id=workspace.backup_volume_id,
        source_path=WORKSPACE_ZIP_PATH,
        dest_volume_id=None,
        dest_path=WORKSPACE_TEMP_ZIP_PATH,
    )

    z = ZipFile(WORKSPACE_TEMP_ZIP_PATH)
    z.extractall(str(Path.home()))


def connect_workspace_ssh(workspace_id: int, private_key_path: str, **kwargs) -> None:
    """Connect to a running workspace via SSH

    Keyword args:
        organization_name (str): override default organization
    """
    workspace = read_workspace(workspace_id, **kwargs)
    if workspace.status != "running":
        raise InvalidWorkspaceError("Workspace must be running.")

    ssh_endpoint = urllib.parse.urlparse(workspace.endpoints.ssh.endpoint)
    os.system(
        f"ssh -p {ssh_endpoint.port} -i {private_key_path} vessl@{ssh_endpoint.hostname}"
    )


def update_vscode_remote_ssh(private_key_path: str) -> None:
    """Update .ssh/config file for VSCode Remote-SSH plugin"""
    workspaces = list_workspaces(status="running")

    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(SSH_CONFIG_PATH, "r"))
    hostname_set = ssh_config.get_hostnames()

    for workspace in workspaces:
        host = f"{workspace.name}-{int(workspace.created_dt.timestamp())}"
        if host in hostname_set:
            continue

        ssh_endpoint = urllib.parse.urlparse(workspace.endpoints.ssh.endpoint)

        config_value = SSH_CONFIG_FORMAT.format(
            host=host,
            hostname=ssh_endpoint.hostname,
            port=ssh_endpoint.port,
            private_key_path=private_key_path,
        )

        with open(SSH_CONFIG_PATH, "a") as f:
            f.write(config_value)
