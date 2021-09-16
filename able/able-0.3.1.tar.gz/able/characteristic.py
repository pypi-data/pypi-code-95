#    Copyright (c)  2021  Allthenticate
"""
Abstraction of the ABleCharacteristic that all backend characteristics inherit from
"""

import abc
import asyncio
import typing
import uuid
from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from able import CharacteristicFlags
    from able.central import ABleCentral
    from able.service import ABleService


class ABleCharacteristic:
    """
    The abstract base class for all of the platform specific implementations of a BLE Characteristic. This class should
    not be used directly, similarly to the `ABleService`, the characteristic that will be imported will be specific
    to which platform ABle is being used on.

    :param characteristic_uuid: the uuid that this characteristic will have, best practice is that it is not the
        same as the service that will own it
    :param value: parameter to initialize the characteristic with a default value, defaults to b'0'
    :param flags: list of permissions/flags to initialize the characteristic with, defaults to read, write and notify
    :param nickname: provide a nickname to the characteristic that will show up in logs, defaults to None
    :param notify_on_write: if `True`, write from centrals will trigger a notification/indication to all subscribed
        centrals
    :ivar bytes value: the current value of the characteristic, setting this value on all backends will trigger an
        update to connected centrals.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        characteristic_uuid: Union[str, uuid.UUID],
        value: bytes = bytes(0),
        flags: List["CharacteristicFlags"] = None,
        nickname: str = None,
        notify_on_write: bool = False,
        **kwargs,
    ):
        """Initialize the BLECharacteristic"""
        from able import CharacteristicFlags  # pylint: disable=import-outside-toplevel

        default_flags = [
            CharacteristicFlags.READ,
            CharacteristicFlags.WRITE,
            CharacteristicFlags.NOTIFY,
        ]
        # Handle the flags
        if flags is None:
            flags = default_flags

        # Handle members shared across all platforms
        self._flags = flags
        self.uuid: str = str(characteristic_uuid)
        self.nickname = nickname
        self.notify_on_write = notify_on_write
        self.client_subscribed: asyncio.Event = asyncio.Event()

        self.service: Optional["ABleService"] = None

        # Work as a mixin
        super().__init__(**kwargs)  # type: ignore

        # Goes last since some __setattr__'s are overloaded
        self.value = value

    def __key(self):
        return str(self.service.uuid), str(self.uuid)

    def __hash__(self):
        return hash(self.__key())

    @abc.abstractmethod
    async def notify_central_of_change(
        self,
        central: "ABleCentral",
        data: bytes,
    ) -> None:
        """
        Virtual method for notifying a central of a change on a characteristic, this is how we handle sending
        data to a central under the hood. The characteristic sets its value to the data then notifies the central
        of the change.

        :param central: the central to notify of the change
        :param data: the data to send to the central by setting the value of the characteristic then notifying
            or indicating only that central of the change
        :return: None
        """
        raise NotImplementedError("This is a purely virtual method...")

    async def wait_for_client_subscription(self, timeout=5) -> None:
        """
        Helper function that will block until a client subscribes to this characteristic. Note that in the current
        implementation this can only check if any client subscribed rather than blocking til as specific central
        subscribes, this is actively being worked on.

        TODO(Bernie): Client specific blocking

        :param timeout: How long to wait before timing out
        """
        await asyncio.wait_for(self.client_subscribed.wait(), timeout=timeout)

    @property
    def flags(self):
        """Get the value of the char flags as a list"""
        return [flag.value for flag in self._flags]

    @property
    def notifying(self):
        """Notifying property checks to see if the client subscribed event has been set"""
        return self.client_subscribed.is_set()

    async def broadcast(self, data: typing.Union[bytes, str]):
        """Virtual method for broadcasting, needs to be implemented on a platform specific basis"""
        raise NotImplementedError
