from dataclasses import dataclass
from typing import List

from ._cfs_type import CFSObjectType


@dataclass
class CFSBucket:
    attributes: List[str] = None
    available_from: str = None
    available_to: str = None
    created: str = None
    description: str = None
    modified: str = None
    name: str = None
    private: bool = None
    publisher_name: str = None
    restricted: bool = None

    def __iter__(self):
        return [CFSFileSet]


@dataclass
class CFSFileSet:
    attributes: List[dict] = None
    available_from: str = None
    available_to: str = None
    bucket_name: str = None
    content_from: str = None
    content_to: str = None
    created: str = None
    files: List[str] = None
    id: str = None
    modified: str = None
    name: str = None
    num_files: int = None
    package_id: str = None
    status: str = None

    def __iter__(self):
        return [CFSFile]


@dataclass
class CFSFile:
    created: str = None
    file_size_in_bytes: int = None
    filename: str = None
    fileset_id: str = None
    href: str = None
    id: str = None
    modified: str = None
    storage_location: dict = None


@dataclass
class CFSPackage:
    bucket_names: List[str] = None
    claims: List[dict] = None
    contact_email: str = None
    created: str = None
    created_by: str = None
    description: str = None
    modified: str = None
    modified_by: str = None
    package_id: str = None
    package_name: str = None
    package_type: str = None
    write_access_users: List[str] = None


data_class_by_type = {
    CFSObjectType.BUCKET: CFSBucket,
    CFSObjectType.PACKAGE: CFSPackage,
    CFSObjectType.FILESET: CFSFileSet,
    CFSObjectType.FILE: CFSFile,
}


class AttributesCFS:
    def __init__(self, type, data: dict):
        data_class = data_class_by_type[type]

        attributes = {
            k: v
            for k, v in data_class.__dict__.items()
            if k[:1] != "_" and k not in data
        }
        data.update(**attributes)
