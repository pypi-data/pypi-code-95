import os
from pathlib import Path

import click

from .env_constants import (
    CONFIG_FILE,
    HOST_SCHEMA_DIR,
    LEVO_CONFIG_DIR,
    LOCAL_SCHEMA_DIR,
)

MSG_WARN_CONFIG_DIR_MOUNT = (
    "Warning: configuration directory has not been mounted correctly.\n"
    + "Levo's Docker image needs "
    + LEVO_CONFIG_DIR
    + " mounted from the host.\n"
    + "Please refer to the CLI documentation.\n"
)


def is_docker():
    """Is this being executed inside a docker container?"""
    path = "/proc/self/cgroup"

    if os.path.exists("/.dockerenv"):
        return True

    if not os.path.isfile(path):
        return False

    with open(path) as docker_cgroup_fob:
        return any("docker" in line for line in docker_cgroup_fob)


def warn_on_invalid_config_mount():
    """Warns user on improper config dir mounts"""
    if not is_docker():
        return  # Nothing to validate

    # Ideally we want to test for os.W_OK as well,
    # however Docker mounts the volume as root, which causes the test to fail
    # So we will have to make do with R&X for now
    if not os.access(LEVO_CONFIG_DIR, os.R_OK | os.X_OK):
        click.echo()
        click.secho(MSG_WARN_CONFIG_DIR_MOUNT, fg="red")
        return

    # Since we cannot test for write access to the dir (see above),
    # test if we can create the config file
    conf_file = Path(CONFIG_FILE)
    try:
        conf_file.touch(mode=0o600, exist_ok=True)
        # check if the config file is incorrectly mounted as a directory
        # e.g. -v $HOME/.config/configstore/levo.json:/home/levo/.config/configstore/levo.json
        if conf_file.is_dir():
            click.echo()
            click.secho(MSG_WARN_CONFIG_DIR_MOUNT, fg="red")
    except:
        click.echo()
        click.secho(MSG_WARN_CONFIG_DIR_MOUNT, fg="red")

    return


def warn_on_invalid_schema_dir_mount():
    """Warns user on improper schema dir mounts"""
    if not is_docker():
        return  # Nothing to validate

    # The host schema dir must be an absolute path
    if not os.path.isabs(HOST_SCHEMA_DIR):
        click.echo()
        click.secho(
            "Warning: envvar HOST_SCHEMA_DIR must be specified as an absolute path when invoking Levo's Docker image.\n"
            + "HOST_SCHEMA_DIR is where OAS schema files are mounted.\n"
            + "Please refer to the CLI documentation.\n",
            fg="red",
        )

    # The local schema dir is a mount for the host schema dir
    if not os.access(LOCAL_SCHEMA_DIR, os.F_OK | os.R_OK):
        click.echo()
        click.secho(
            "Warning: host schema directory has not been mounted correctly.\n"
            + "Levo's Docker image needs a mount where OAS schema files reside.\n"
            + "Please refer to the CLI documentation.\n",
            fg="red",
        )

    return


def warn_on_invalid_env_and_mounts() -> None:
    """Warns the user on improper volume bind mounts & ENV vars"""
    warn_on_invalid_config_mount()
    warn_on_invalid_schema_dir_mount()
    return


def _is_path_relative(path):
    """Is the specfified path a relative path in Windows OR Posix formats?
    returns bool
    """
    if type(path) is not str:
        return False

    if path == "":
        return False

    # Is this a Windows drive like c:\?
    if len(path) >= 3 and path[0].isalpha() and path[1] == ":" and path[2] == "\\":
        return False

    if (
        path.startswith("./")
        or path.startswith("../")
        or path.startswith(".\\")
        or path.startswith("..\\")
        or path[0].isalnum()
    ):
        return True

    return False


def convert_host_abs_path_to_container(host_abs_path):
    """Given a host absolute file path (str), calculate the absolute path of the file,
    (mounted) within the container
    Returns the absolute path (str) or None
    """
    if not is_docker():
        return host_abs_path

    if type(host_abs_path) is not str:
        return None

    if host_abs_path == "":
        return None

    # Is this a relative path?
    if _is_path_relative(host_abs_path):
        return None

    # The host path prefix needs to  match the prefix in the path
    if host_abs_path.find(HOST_SCHEMA_DIR) != 0:
        return None

    converted_path = host_abs_path
    # Replace the host path prefix with mapped container prefix
    converted_path = converted_path.replace(HOST_SCHEMA_DIR, LOCAL_SCHEMA_DIR + "/", 1)
    converted_path = converted_path.replace("//", "/")  # Get rid of double slashes
    # Convert Windows format to Posix
    converted_path = converted_path.replace("\\", "/")

    return converted_path
