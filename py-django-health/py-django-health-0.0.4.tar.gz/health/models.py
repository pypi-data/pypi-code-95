import typing
import pydantic

from health.consts import Status

__all__ = [
    'ComponentHealth',
    'DiskHealth',
    'DatabaseHealth',
    'CacheHealth'
]


class ComponentHealth(pydantic.BaseModel):
    """
    Base info model
    """
    type: str
    status: Status = Status.ALIVE


class DiskHealth(ComponentHealth, pydantic.BaseModel):
    """
    Disk info model
    """
    type = "DISK"
    total: typing.Optional[int]
    free: typing.Optional[int]
    used: typing.Optional[int]


class DatabaseHealth(ComponentHealth, pydantic.BaseModel):
    """
    Database info model
    """
    type = "DATABASE"
    name: typing.Optional[str]
    uri: typing.Optional[str]
    vendor: typing.Optional[str]


class CacheHealth(ComponentHealth, pydantic.BaseModel):
    """
    Cache info model
    """
    type = "CACHE"
    name: typing.Optional[str]
    backend: typing.Optional[str]
