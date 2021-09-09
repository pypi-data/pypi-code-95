import json
import os
import tempfile

from unittest import TestCase

from zeero.plugins.common import (
    Artifact,
    save_artifact,
    get_artifact,
    secret_from_literal,
    secret_from_file
)


def test_save_artifact_with_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        save_artifact(Artifact.FILE, "test.txt", "test", temp_dir)
        path = os.path.join(temp_dir, "test.txt")
        with open(path, "r", encoding="utf-8") as artifact:
            assert artifact.read() == "test"


def test_save_artifact_with_value():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "artifacts")
        # call twice to cover non-existing and pre-existing values.json
        # code paths. these calls should be idempotent given the same
        # key/value is used
        save_artifact(Artifact.VALUE, "key", "value", path)
        save_artifact(Artifact.VALUE, "key", "value", path)

        values_json = os.path.join(path, "values.json")
        with open(values_json, "r", encoding="utf-8") as artifact_values:
            values = json.loads(artifact_values.read())
            assert values["key"] == "value"


def test_get_artifact():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "values.json")
        with open(path, "w", encoding="utf-8") as values_file:
            values_file.write('{"key": "value"}')

        assert get_artifact("key", temp_dir) == "value"


def test_secret_from_literal():
    assert secret_from_literal("test") == "dGVzdA=="


def test_secret_from_file():
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(b"test")
    tf.close()

    try:
        assert secret_from_file(tf.name) == "dGVzdA=="
    finally:
        os.remove(tf.name)