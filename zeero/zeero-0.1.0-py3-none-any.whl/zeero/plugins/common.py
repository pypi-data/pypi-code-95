"""This module contains common helper classes for creating plugins"""

import base64
import enum
import io
import json
import os
import pathlib


ARTIFACTS_PATH = "/tmp/artifacts"
PARAMETERS_PATH = "/tmp/parameters.yaml"


class Status(enum.Enum):
    """Status represents the status of the plugin.
    """

    PROGRESSING = 0
    COMPLETE = 1
    FAILED = 2


class Artifact(enum.Enum):
    """Artifact represents an artifact generated during plugin execution.
    """

    FILE = 0
    VALUE = 1


def run_command(command: str, args: list[str], error_msg: str, debug: bool = False):
    """run_command runs the command and returns the output
    """

    out = io.StringIO()
    err = io.StringIO()

    try:
        command(*args, _err=err, _out=out) # pylint: disable=not-callable
    except Exception: # pylint: disable=broad-except
        if debug is True:
            return None, f"{error_msg}: {err.getvalue()}"

        return None, error_msg

    return out.getvalue(), None


def save_artifact(kind: Artifact, name: str = None, data: str = None, path: str = None):
    """save_artifact saves the file or value artifact.
    """

    if not os.path.exists(path):
        os.makedirs(path)

    if kind is Artifact.FILE:
        with open(os.path.join(path, name), "w", encoding="utf-8") as artifact:
            artifact.write(data)

    if kind is Artifact.VALUE:
        path = os.path.join(path, "values.json")
        pathlib.Path(path).touch()

        with open(path, "r+", encoding="utf-8") as artifact_values:
            contents = artifact_values.read()
            if contents == "":
                values = {}
            else:
                values = json.loads(contents)

            values[name] = data
            artifact_values.seek(0)
            artifact_values.write(json.dumps(values))


def get_artifact(key: str, path: str):
    """get_artifact get the value artifact from the artifact values.
    """

    values_path = os.path.join(path, "values.json")
    with open(values_path, encoding="utf-8") as values_file:
        values = json.loads(values_file.read())
        return values.get(key)


def secret_from_literal(value):
    """secret_from_literal returns the base64 encoded secret value.
    """

    return base64.b64encode(value.encode()).decode()


def secret_from_file(path):
    """secret_from_file returns the base64 encoded secret value from the
    file at the provided path.
    """

    with open(path, "rb") as secret_file:
        return base64.b64encode(secret_file.read()).decode()
