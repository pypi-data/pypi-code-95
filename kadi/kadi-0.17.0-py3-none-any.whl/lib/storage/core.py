# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from abc import ABC
from abc import abstractmethod

from flask import current_app


class BaseStorage(ABC):
    """Base class for all storage providers.

    :param max_size: (optional) The maximum file size for the storage to accept.
    """

    # pylint: disable=missing-function-docstring

    def __init__(self, max_size=None):
        self.max_size = max_size

    @abstractmethod
    def exists(self, filepath):
        pass

    @abstractmethod
    def open(self, filepath, mode="rb", encoding=None):
        pass

    @abstractmethod
    def close(self, file):
        pass

    @abstractmethod
    def save(self, dst, file_or_src, append=False):
        pass

    @abstractmethod
    def move(self, src, dst):
        pass

    @abstractmethod
    def delete(self, filepath):
        pass

    @abstractmethod
    def get_mimetype(self, filepath):
        pass

    @abstractmethod
    def get_size(self, filepath):
        pass

    @abstractmethod
    def validate_size(self, filepath, size, op="=="):
        pass

    @abstractmethod
    def get_checksum(self, filepath):
        pass

    @abstractmethod
    def verify_checksum(self, filepath, expected):
        pass


def create_storage(storage_type="local", **kwargs):
    r"""Create a storage provider based on a given storage type.

    :param storage_type: (optional) The type of storage provider to create.
    :param \**kwargs: Additional keyword arguments to pass on to the storage provider.
    :return: The new storage provider instance or ``None`` if the given storage type is
        invalid.
    """
    from .local import LocalStorage

    if storage_type == "local":
        return LocalStorage(**kwargs)

    return None


def create_filepath(file_identifier, storage_type="local"):
    """Create a path from a file identifier suitable for storing files.

    The structure of the path is dependent on the given storage type.

    :param file_identifier: The identifier of the file. This should generally be a
        file's internal, unique ID suitable for an actual file name, e.g. a UUID like in
        :attr:`.File.id`.
    :param storage_type: (optional) The type of the file's storage.
    :return: The created file path or ``None`` if the given storage type is invalid.
    """
    from .local import LocalStorage

    if storage_type == "local":
        filepath = LocalStorage.filepath_from_name(
            file_identifier, dir_len=2, num_dirs=3
        )
        return os.path.join(current_app.config["STORAGE_PATH"], filepath)

    return None
