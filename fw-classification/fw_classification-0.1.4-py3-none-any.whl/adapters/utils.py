"""Adapter utilities."""
from typing import List, Optional

from pydantic import BaseModel


class ContainerReference(BaseModel):  # pragma: no cover
    """Container reference object."""

    id: str
    type: str


class Location(BaseModel):  # pragma: no cover
    """Location in docker container."""

    path: str
    name: str


class Origin(BaseModel):  # pragma: no cover
    """Origin of file."""

    type: str
    id: Optional[str]


class FileObject(BaseModel):  # pragma: no cover
    """File object."""

    type: Optional[str]
    mimetype: str
    modality: Optional[str]
    classification: dict = {}
    tags: List[str] = []
    info: dict = {}
    size: Optional[int]
    zip_member_count: Optional[int]
    version: int
    file_id: Optional[str]
    origin: Optional[Origin] = None


class FileInput(BaseModel):
    """Full file object as it shows up in config.json."""

    hierarchy: ContainerReference
    object: FileObject
    location: Location
    base: str = "file"
