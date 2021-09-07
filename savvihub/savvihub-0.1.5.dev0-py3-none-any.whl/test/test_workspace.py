import datetime
import os
from test.conftest import USE_MOCK

import pytest
from mock import Mock, patch

import savvihub
from savvihub.util.constant import SSH_CONFIG_FORMAT
from savvihub.util.exception import InvalidWorkspaceError


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestWorkspace:
    def test_read_workspace(self):
        # Must create first
        pass

    def test_list_workspaces(self):
        savvihub.list_workspaces()


def test_backup_workspace():
    # Test fail
    config_instance_mock = Mock()
    config_instance_mock.workspace = None
    config_mock = Mock(return_value=config_instance_mock)

    with patch.object(savvihub.workspace, "VesslConfigLoader", config_mock):
        with pytest.raises(InvalidWorkspaceError):
            savvihub.backup_workspace()

    # TODO: Add test success


def test_restore_workspace():
    # Test fail
    config_instance_mock = Mock()
    config_instance_mock.workspace = None
    config_mock = Mock(return_value=config_instance_mock)

    with patch.object(savvihub.workspace, "VesslConfigLoader", config_mock):
        with pytest.raises(InvalidWorkspaceError):
            savvihub.restore_workspace()

    # TODO: Add test success


def test_connect_workspace_ssh():
    workspace_id = 1234
    private_key_path = "/path/to/key"

    # Test fail
    workspace_mock = Mock()
    workspace_mock.status = "terminated"

    read_workspace_ = patch.object(
        savvihub.workspace, "read_workspace", return_value=workspace_mock
    )

    with read_workspace_:
        with pytest.raises(InvalidWorkspaceError):
            savvihub.connect_workspace_ssh(workspace_id, private_key_path)

    # Test success
    port = 1234
    hostname = "tcp.hostname.com"

    workspace_mock = Mock()
    workspace_mock.status = "running"
    workspace_mock.endpoints.ssh.endpoint = f"tcp://{hostname}:{port}"

    read_workspace_ = patch.object(
        savvihub.workspace, "read_workspace", return_value=workspace_mock
    )
    system_ = patch("savvihub.workspace.os.system")

    with read_workspace_, system_:
        savvihub.connect_workspace_ssh(workspace_id, private_key_path)
        savvihub.workspace.os.system.assert_called_with(
            f"ssh -p {port} -i {private_key_path} vessl@{hostname}"
        )


def test_update_vscode_remote_ssh():
    # Setup
    ssh_config_path = "test/ssh_config"
    with open(ssh_config_path, "w+"):
        pass

    private_key_path = "/path/to/key"
    name = "vessl_workspace"
    created_dt = datetime.datetime.now()
    port = 1234
    hostname = "tcp.hostname.com"
    host = f"{name}-{int(created_dt.timestamp())}"

    workspace_mock = Mock()
    workspace_mock.name = name
    workspace_mock.created_dt = created_dt
    workspace_mock.endpoints.ssh.endpoint = f"tcp://{hostname}:{port}"

    list_workspaces_ = patch.object(
        savvihub.workspace, "list_workspaces", return_value=[workspace_mock]
    )
    paramiko_ = patch.object(savvihub.workspace, "paramiko")
    ssh_config_format_ = patch.object(
        savvihub.workspace, "SSH_CONFIG_PATH", ssh_config_path
    )

    with list_workspaces_, paramiko_, ssh_config_format_:
        savvihub.update_vscode_remote_ssh(private_key_path)

    with open(ssh_config_path, "r") as f:
        assert f.read() == SSH_CONFIG_FORMAT.format(
            host=host,
            hostname=hostname,
            port=port,
            private_key_path=private_key_path,
        )

    # Teardown
    try:
        os.remove(ssh_config_path)
    except OSError:
        pass
