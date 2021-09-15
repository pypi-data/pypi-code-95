import pytest

from jelastic_client import ControlClient, JpsClient
from jelastic_client.core.exceptions import JelasticClientException
from test_utils.manifest_data import get_manifest_data


def test_jps_client_install_from_file_valid_manifest_creates_environment(
        control_client: ControlClient,
        jps_client: JpsClient,
        valid_manifest: str,
        new_env_name: str):
    # Arrange

    # Act
    jps_client.install_from_file(valid_manifest, new_env_name)

    # Assert
    env_info = control_client.get_env_info(new_env_name)
    assert env_info.exists()


def test_jps_client_install_from_file_valid_manifest_makes_environment_run(
        control_client: ControlClient,
        jps_client: JpsClient,
        valid_manifest: str,
        new_env_name: str):
    # Arrange

    # Act
    jps_client.install_from_file(valid_manifest, new_env_name)

    # Assert
    env_info = control_client.get_env_info(new_env_name)
    assert env_info.is_running()


def test_jps_client_install_from_file_valid_manifest_returns_success_text(
        jps_client: JpsClient,
        valid_manifest: str,
        new_env_name: str):
    # Arrange

    # Act
    actual_success_text = jps_client.install_from_file(
        valid_manifest, new_env_name)

    # Assert
    expected_success_text = "<strong>Field1</strong>: Value1<br />\n<strong>Field2</strong>: Value2"
    assert expected_success_text == actual_success_text


def test_jps_client_install_from_file_invalid_manifest_raises_exception(
        jps_client: JpsClient,
        invalid_manifest: str,
        new_env_name: str):
    # Arrange

    # Act / Assert
    with pytest.raises(JelasticClientException):
        jps_client.install_from_file(invalid_manifest, new_env_name)


def test_jps_client_install_from_file_non_existent_manifest_raises_exception(
        jps_client: JpsClient,
        non_existent_manifest: str,
        new_env_name: str):
    # Arrange

    # Act / Assert
    with pytest.raises(OSError):
        jps_client.install_from_file(non_existent_manifest, new_env_name)


def test_jps_client_install_from_file_manifest_with_settings_takes_settings_into_account(
        jps_client: JpsClient,
        manifest_with_settings: str):
    # Arrange
    expected_settings = {
        "field1": "the value 1",
        "field2": "the value 2"
    }

    # Act
    success_text = jps_client.install_from_file(
        manifest_with_settings,
        settings=expected_settings)
    manifest_data = get_manifest_data(success_text)

    # Assert
    for field in expected_settings:
        assert field in manifest_data
        assert expected_settings[field] == manifest_data[field]


def test_jps_client_get_engine_version_returns_supported_engine_version(
        jps_client: JpsClient,
        supported_jelastic_version: str):
    # Arrange

    # Act
    actual_version = jps_client.get_engine_version()

    # Assert
    assert supported_jelastic_version == actual_version
