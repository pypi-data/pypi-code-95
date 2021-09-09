import collections
import json
import os
import shutil
import tempfile

from unittest import mock, TestCase

from zeero.plugins.common import Artifact, Status, secret_from_literal
from zeero.plugins.factory import ARTIFACTS_PATH, ManifestBuilder, set_status


def test_set_status():
    tf = tempfile.NamedTemporaryFile(delete=True)
    tf.close()
    set_status(Status.PROGRESSING, "zeero", "progressing", 10, tf.name)
    with open(tf.name, "r") as tf:
        expect = {
            "type": "factory-status-update",
            "data": {
                "source": "zeero",
                "status": 0x0,
                "message": "progressing",
                "progress": 10
            }
        }
        assert json.loads(open(tf.name).read()) == expect


class TestManifestBuilder(TestCase):
    @mock.patch("zeero.plugins.common.io")
    @mock.patch("zeero.plugins.factory.sh")
    def test_clone_operator(self, mock_sh, mock_io):
        builder = ManifestBuilder("test")
        repo_dir, err = builder.clone_operator("https://git.com/test/my-operator")
        shutil.rmtree(repo_dir, ignore_errors=True)
        assert err is None

        mock_sh.git.assert_called_with(
            "clone",
            "https://git.com/test/my-operator",
            repo_dir,
            _err=mock_io.StringIO(),
            _out=mock_io.StringIO()
        )

    @mock.patch("zeero.plugins.factory.sh")
    def test_clone_operator_with_error(self, mock_sh):
        def raise_mock_error(*args):
            raise Exception()

        mock_sh.git.side_effect = raise_mock_error
        builder = ManifestBuilder("test")
        repo, err = builder.clone_operator("https://git.com/test/my-operator")
        shutil.rmtree(repo, ignore_errors=True)

        assert err == "error cloning the operator repository"

    @mock.patch("zeero.plugins.common.io")
    @mock.patch("zeero.plugins.factory.sh")
    def test_clone_operator_with_debug_error(self, mock_sh, mock_io):
        mock_err = "ERROR: (gcloud.test.error) error"
        mock_io.StringIO().getvalue.side_effect = lambda: mock_err
        def raise_mock_error(*args, **kwargs):
            kwargs["_err"].write(mock_err)
            raise Exception()

        mock_sh.git.side_effect = raise_mock_error
        builder = ManifestBuilder("test")
        repo, err = builder.clone_operator(
            "https://git.com/test/my-operator",
            debug=True
        )
        shutil.rmtree(repo, ignore_errors=True)

        assert err == f"error cloning the operator repository: {mock_err}"

    @mock.patch("zeero.plugins.common.io")
    @mock.patch("zeero.plugins.factory.sh")
    @mock.patch("zeero.plugins.factory.tempfile")
    def test_kustomize_build(self, mock_tempfile, mock_sh, mock_io):
        tempdir_path = "/tmp/flz9b4a9g4a"
        os.makedirs(tempdir_path, exist_ok=True)
        builder = ManifestBuilder("test")
        Tempdir = collections.namedtuple("Tempdir", ("name",))
        mock_tempdir = Tempdir(tempdir_path)
        mock_tempfile.TemporaryDirectory.return_value = mock_tempdir
        mock_io.StringIO().getvalue.side_effect = lambda: "kustomize-build"

        try:
            manifest, err = builder.build_operator_manifest(
                "https://git.com/test/my-operator",
                "config/default/kustomization.yaml"
            )
        finally:
            shutil.rmtree(tempdir_path)

        assert err is None
        assert manifest == "kustomize-build"

        mock_sh.git.assert_called_with(
            "clone",
            "https://git.com/test/my-operator",
            mock_tempdir.name,
            _err=mock_io.StringIO(),
            _out=mock_io.StringIO()
        )

        mock_sh.kustomize.assert_called_with(
            "build",
            os.path.join(mock_tempdir.name, "config/default/kustomization.yaml"),
            _err=mock_io.StringIO(),
            _out=mock_io.StringIO()
        )

    def test_add_manifest(self):
        spec = {
            "provider": "google",
            "domain_filters": ["test.com"],
            "google": {"project": "test"}
        }
        builder = ManifestBuilder("test")
        builder.add_manifest("external-dns", "dns.zeero.io/v1", "ExternalDNS", spec)
        assert builder._manifests[0] == {
            "apiVersion": "dns.zeero.io/v1",
            "kind": "ExternalDNS",
            "metadata": {
                "name": "external-dns",
                "namespace": "test"
            },
            "spec": {
                "domain_filters": ["test.com"],
                "google": {
                    "project": "test"
                },
                "provider": "google"
            }
        }

    def test_add_secret(self):
        data = {"test": secret_from_literal("test")}
        builder = ManifestBuilder("test")
        builder.add_secret("test", data)
        assert builder._secrets[0] == {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "test",
                "namespace": "test"
            },
            "data": {
                "test": "dGVzdA=="
            },
            "immutable": True
        }

    @mock.patch("zeero.plugins.factory.sh")
    @mock.patch("zeero.plugins.common.io")
    def test_build_manifests(self, mock_io, mock_sh):
        spec = {
            "provider": "google",
            "domain_filters": ["test.com"],
            "google": {"project": "test"}
        }
        data = {"test": secret_from_literal("test")}
        mock_io.StringIO().getvalue.side_effect = lambda: "kustomize-build"
        builder = ManifestBuilder("test")
        builder.add_manifest("external-dns", "dns.zeero.io/v1", "ExternalDNS", spec)
        builder.add_secret("test", data)
        err = builder.build_manifests("https://git.com/test/my-operator", "path")

        assert err is None

        artifacts_path = os.path.join(ARTIFACTS_PATH, "manifests.yaml")
        with open(artifacts_path, "r", encoding="utf-8") as artifacts:
            assert artifacts.read() == """---
kustomize-build
---
apiVersion: v1
kind: Namespace
metadata:
  name: test
---
apiVersion: dns.zeero.io/v1
kind: ExternalDNS
metadata:
  name: external-dns
  namespace: test
spec:
  provider: google
  domain_filters:
  - test.com
  google:
    project: test
---
apiVersion: v1
kind: Secret
metadata:
  name: test
  namespace: test
data:
  test: dGVzdA==
immutable: true
---
"""

    @mock.patch("zeero.plugins.factory.sh")
    def test_build_manifests_with_error(self, mock_sh):
        def raise_mock_error(*args):
            raise Exception()

        mock_sh.git.side_effect = raise_mock_error
        builder = ManifestBuilder("test")
        err = builder.build_manifests("https://git.com/test/my-operator", "path")
        assert err == "error cloning the operator repository"
