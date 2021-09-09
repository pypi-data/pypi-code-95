"""This module contains classes to build factory manifests"""

import io
import json
import os
import uuid

import sh

from ruamel.yaml import YAML

from .common import (
    ARTIFACTS_PATH,
    Artifact,
    Status,
    run_command,
    save_artifact,
)

DEBUG = bool(os.environ.get("DEBUG", False))
STATUS_EVENT_STREAM="/tmp/status"


def set_status(status: Status, source: str, message: str, progress: int):
    """set_status writes the factory status update event to the event stream.
    """

    with open(STATUS_EVENT_STREAM, "a+", encoding="utf-8") as event_stream:
        status_event = json.dumps({
            "type": "factory-status-update",
            "data": {
                "source": source,
                "status": status.value,
                "message": message,
                "progress": progress
            }
        })
        print(status_event, file=event_stream)


class ManifestBuilder():
    """ManifestBuilder builds a set of kubernetes compliant resource manifests.
    """

    def __init__(self, namespace):
        self._secrets = []
        self._manifests = []
        self._namespace = namespace

    @staticmethod
    def clone_operator(url: str, debug: bool = False):
        """clone_operator clones the operator repository
        """

        repo_dir = f"/tmp/{uuid.uuid1()}"
        _, err = run_command(
            sh.git, # pylint: disable=no-member
            ("clone", url, repo_dir),
            "error cloning the operator repository",
            debug
        )

        if err is not None:
            return None, err

        return repo_dir, None

    def build_operator_manifest(self, url: str, path: str, debug: bool = False):
        """build_operator_manifest builds the operator kustomize manifests
        """

        repo_dir, err = self.clone_operator(url, debug)
        if err is not None:
            return None, err
        return run_command(
            sh.kustomize, # pylint: disable=no-member
            ("build", os.path.join(repo_dir, path)),
            "error running kustomize build",
            debug
        )

    def add_manifest(self, name: str, api: str, kind: str, spec: dict):
        """add_manifest adds the manifest to the builder manifests.
        """

        manifest = {
            "apiVersion": api,
            "kind": kind,
            "metadata": {
                "name": name,
                "namespace": self._namespace
            },
            "spec": spec
        }
        self._manifests.append(manifest)

    def add_secret(self, name: str, data: dict):
        """add_secret adds the secret to the builder manifests.
        """

        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": self._namespace
            },
            "data": data,
            "immutable": True
        }
        self._secrets.append(secret)

    def build_manifests(self, url: str, path: str, debug: bool = False):
        """build_manifests builds the output resource manifests.
        """

        manifests_io = io.StringIO()
        operator_manifest, err = self.build_operator_manifest(url, path, debug)
        if err is not None:
            return err

        manifests_io.write(f"{operator_manifest}\n---\n")

        yaml = YAML()
        yaml.dump({
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self._namespace
            }
        }, manifests_io)
        manifests_io.write("---\n")

        for manifest in self._manifests:
            yaml.dump(manifest, manifests_io)
            manifests_io.write("---\n")

        for secret in self._secrets:
            yaml.dump(secret, manifests_io)
            manifests_io.write("---\n")

        manifests = "---\n" + manifests_io.getvalue()
        save_artifact(Artifact.FILE, "manifests.yaml", manifests, ARTIFACTS_PATH)

        return None
