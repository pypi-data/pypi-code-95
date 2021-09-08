from typing import Optional
from dataclasses import dataclass

from energytt_platform.bus import Message
from energytt_platform.models.auth import MeteringPointDelegate


@dataclass
class DelegateGranted(Message):
    """
    TODO
    """
    subject: str


@dataclass
class DelegateRevoked(Message):
    """
    TODO
    """
    subject: str


# -- Delegates ---------------------------------------------------------------


@dataclass
class MeteringPointOwnerUpdate(Message):
    """
    TODO
    TODO Received by auth-service to determine the owner, who can grant delegates on this GSRN number
    """
    gsrn: str
    subject: Optional[str]


@dataclass
class MeteringPointDelegateGranted(Message):
    """
    An actor (identified by its subject) has been delegated
    access to a MeteringPoint.
    """
    delegate: MeteringPointDelegate


@dataclass
class MeteringPointDelegateRevoked(Message):
    """
    An actor (identified by its subject) has had its delegated
    access to a MeteringPoint revoked.
    """
    delegate: MeteringPointDelegate
