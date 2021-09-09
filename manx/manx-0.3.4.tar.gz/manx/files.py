import hashlib
import importlib
import os
import re
import time
from operator import attrgetter
from typing import Iterator, Tuple

from manx.exceptions import ManxException

filename_pattern = re.compile(r"(\d+)[-_]?([\w-]*)\.py")
non_identifier = re.compile(r"[^\w-]+")


class MigrationFile:
    def __init__(self, stamp, name, path, hash_=None, module=None, config=None):
        self.stamp = stamp
        self.name = name
        self.path = path
        self.hash_ = hash_
        self.module = module
        self.config = config

    def is_after(self, other: "MigrationFile"):
        if other is None:
            return False
        return self.stamp > other.stamp

    def is_equal(self, other: "MigrationFile"):
        if other is None:
            return False

        if self.stamp == other.stamp:
            if self.hash_ != other.hash_:
                msg = f"Hash mismatch in file {self.path}. It has likely been modified."
                raise ManxException(msg)
            else:
                return True
        else:
            return False

    def to_meta_doc(self, alias, config):
        millis = int(time.time_ns() / 1_000_000)
        return {
            "stamp": self.stamp,
            "name": self.name,
            "sha3": self.hash_,
            "applied_at": millis,
            "alias": alias,
            "config": config,
        }

    def __str__(self):
        return f"Migration [{self.stamp} {self.name}]"


def get_python_files(package: str) -> Iterator[MigrationFile]:
    directory = package.replace(".", "/")
    files = os.listdir(directory)

    migration_files = []
    stamps = set()
    for filename in files:
        match = parse_file_name(filename)
        if match:
            mf = migration_from_file(match, package, directory, filename)
            if mf.stamp in stamps:
                msg = f"Multiple files with stamp={mf.stamp}"
                raise ManxException(msg)
            else:
                migration_files.append(mf)
                stamps.add(mf.stamp)

    migration_files.sort(key=attrgetter("stamp"))
    return iter(migration_files)


def migration_from_file(match, package, directory, filename) -> MigrationFile:
    stamp, label = match
    full_path = os.path.join(directory, filename)
    hash_ = _hash(full_path)
    module = importlib.import_module(f"{package}.{filename[:-3]}")

    return MigrationFile(stamp, label, full_path, hash_, module)


def parse_file_name(name: str) -> Tuple[int, str]:
    match_ = filename_pattern.match(name)
    if match_:
        stamp = int(match_.group(1))
        label = match_.group(2) or None
        return stamp, label
    return None


def _hash(file: str) -> str:
    sha3 = hashlib.sha3_224()
    with open(file, "rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            sha3.update(chunk)
    return sha3.hexdigest()
