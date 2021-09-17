#    Copyright (c)  2021  Allthenticate
"""
References for this implementation of a Bluez Characteristic using dbus-next

GATT Characteristic: https://gitlab.com/allthenticate/dependencies/bluez/-/blob/master/doc/gatt-api.txt
BLE Core Specification: https://www.bluetooth.com/specifications/specs/core-specification/
"""

# Native dependencies
import asyncio
import logging
import multiprocessing
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

# Other dependencies
from dbus_next import Variant
from dbus_next.constants import PropertyAccess
from dbus_next.service import ServiceInterface, dbus_property, method

# Able dependencies
from able.bluezdbus import BluezServiceInterfaces
from able.bluezdbus.service import BluezService
from able.bluezdbus.utils import parse_identifier_from_path

# This is a cyclic import
from able.characteristic import ABleCharacteristic

if TYPE_CHECKING:
    from able.bluezdbus.application import BluezApplication
    from able.central import ABleCentral

logger = logging.getLogger(name=__name__)


class BlueZCharacteristicFlags(Enum):
    """Enum for possible characteristic flags and permissions"""

    AUTHENTICATED_SIGNED_WRITES = "authenticated_signed_writes"
    AUTHORIZE = "authorize"
    BROADCAST = "broadcast"
    ENCRYPT_AUTHENTICATED_READ = "encrypt_authenticated_read"
    ENCRYPT_AUTHENTICATED_WRITE = "encrypt_authenticated_write"
    ENCRYPT_READ = "encrypt_read"
    ENCRYPT_WRITE = "encrypt_write"
    EXTENDED_PROPERTIES = "extended_properties"
    INDICATE = "indicate"
    NOTIFY = "notify"
    READ = "read"
    RELIABLE_WRITE = "reliable_write"
    SECURE_READ = "secure_read"
    SECURE_WRITE = "secure_write"
    WRITABLE_AUXILIARIES = "writable_auxiliaries"
    WRITE = "write"
    WRITE_WITHOUT_RESPONSE = "write_without_response"


# noinspection PyPep8Naming
class BluezCharacteristic(ABleCharacteristic, ServiceInterface):
    """
    Class implementation of a BlE GATT Characteristic using Dbus-Next
    """

    def __init__(
        self,
        characteristic_uuid: uuid.UUID,
        value=bytes(0),
        flags=None,
        nickname: str = None,
        notify_on_write: bool = False,
    ):
        super().__init__(
            characteristic_uuid,
            value,
            flags,
            nickname,
            notify_on_write,
            name=BluezServiceInterfaces.GATT_CHARACTERISTIC_INTERFACE.value,
        )

        # DBus Members
        self._path = None

        # Additional Members
        self.application: Optional["BluezApplication"] = None
        self.subscribed_clients: int = 0
        self.subscribed_clients_lock: multiprocessing.synchronize.Lock = (
            multiprocessing.Lock()
        )

        # Keep track of whether or not this characteristic is the char for socket comms
        self.is_marked = False

        logger.debug(f"Setting up characteristic with flags: {self.flags}")

    def __str__(self):
        return (
            f"BluezCharacteristic [{self.uuid}]"
            if self.nickname is None
            else self.nickname
        )

    def __repr__(self):
        return str(self)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

        # If the key is value, we need to emit the properties changed to bluez so it catches the change
        if key == "value":
            self.emit_properties_changed({"Value": self.value})

    @dbus_property(PropertyAccess.READ, name="UUID")
    def _uuid(self) -> "s":  # type: ignore
        """
        Dbus property to return the UUID of this characteristic.

        :return: 128-bit characteristic UUID.
        """
        return str(self.uuid)

    @dbus_property(PropertyAccess.READ, name="Service")
    def _service(self) -> "o":  # type: ignore
        """
        Dbus property to read the object path of the service this characteristic is owned by.

        :return: Object path of the GATT service the characteristic
                        belongs to.
        """
        if not isinstance(self.service, BluezService):
            raise RuntimeError(
                f"Service of characteristic is not of type BluezService, is {self.service!r}"
            )

        return self.service.path

    @dbus_property(PropertyAccess.READ, name="Value")
    def _value(self) -> "ay":  # type: ignore
        """
        Dbus property to read the current value of the characteristic.

        :return: The cached value of the characteristic. This property
                        gets updated only after a successful read request and
                        when a notification or indication is received, upon
                        which a PropertiesChanged signal will be emitted.
        """
        return self.value

    @dbus_property(PropertyAccess.READ, name="Notifying")
    def _notifying(self) -> "b":  # type: ignore
        """
        Dbus property to read whether or not this characteristic is notifying.

        :return: True, if notifications or indications on this
                        characteristic are currently enabled.
        """
        return self.notifying

    @dbus_property(PropertyAccess.READ, name="Flags")
    def _get_flags(self) -> "as":  # type: ignore
        """
        Dbus property to get the flags associated with the characteristic.

        :return: Defines how the characteristic value can be used.
        """
        return self.flags

    @method(name="ReadValue")
    def _get_value(self, options: "a{sv}") -> "ay":  # type: ignore
        """
        Handles the request from bluez to read the value of the characteristic.

        TODO(Bernie): How should we treat the options here, should we update mtu and such?

        :param options: A dictionary of options provided by bluez regarding the read request. Possible
            values are: "offset": uint16 offset, "mtu": Exchanged MTU (Server only),
            "device": Object Device (Server only)
        :return: the value of the characteristic
        """
        logger.debug(f"Read occurred with options: {options} to {self}")
        return self.value

    @method(name="WriteValue")
    def _set_value(self, value: "ay", options: "a{sv}"):  # type: ignore
        """
        Handles the request from bluez over dbus to write a value to the characteristic.

        TODO(Bernie): Evaluate if we should treat writes from centrals which were connected before the
            service started similar to connects

        :param value: The value to update the characteristic to
        :param options: a dictionary of options regarding the write request. Possible values are:
            "offset": Start offset, "type": `str`, "mtu": Exchanged MTU (Server only),
            "device": Device path (Server only), "link": Link type (Server only),
            "prepare-authorize": `True` if prepare
        :return: None
        """
        if self.application is None:
            raise RuntimeError(
                "No application bound for characteristic, unable to perform actions"
            )

        logger.debug(f"Write occurred to {self} [data: [{value[:20]}]")

        identifier: str = parse_identifier_from_path(options.get("device").value)

        # Fetch the central from the app, if not found
        if identifier not in self.application.connected_centrals:
            logger.warning(
                f"Received a write from {identifier} who we aren't tracking, ignoring"
            )
            return

        # Add the data to the recv queue
        writer: "ABleCentral" = self.application.connected_centrals[identifier]
        asyncio.create_task(writer.char_queues[hash(self)].put(value))

        # Update the MTU if it is provided in the options
        mtu = options.get("mtu", Variant("b", False)).value
        if mtu:
            logger.debug(
                f"Updating {writer} mtu to {mtu} after a write to a characteristic"
            )
            writer.mtu = mtu

        if self.notify_on_write:
            logger.debug(
                f"Updating value of {self} after a write and notifying all centrals subscribed"
            )
            self.value = value
        else:
            logger.debug(f"Not notifying after updating value of {self}")
            self.__dict__["value"] = value

    @method(name="StartNotify")
    def _enable_notifications(self):
        """
        Handles request from bluez which indicates that a central wants to be notified on this characteristic.

        :return: None
        """
        logger.debug(f"{self} is now notifying, incrementing the subscribed semaphore.")

        # Always start notifying and mark as ready
        self.client_subscribed.set()

        # Update the semaphore
        # with self.subscribed_clients_lock:
        self.subscribed_clients += 1

    @method(name="StopNotify")
    def _stop_notify(self):
        """
        Handles the request from bluez which indicates that a central no longer wants to be notified on this
        characteristic.

        :return: None
        """
        logger.debug(
            f"A client has unsubscribed to {self}, decrementing the subscribed semaphore."
        )

        # Decrement the semaphore
        # with self.subscribed_clients_lock:
        self.subscribed_clients -= 1

        # If no more clients are subscribed, stop notifying and clear the ready event
        if self.subscribed_clients <= 0:
            logger.debug(f"There no longer any clients subscribed to {self}")
            self.client_subscribed.clear()

    async def notify_central_of_change(  # pylint: disable=arguments-differ, unused-argument
        self, central: "ABleCentral", data: bytes, *args
    ) -> None:
        """
        Makes a bluez call to notify only one central of a change to this characteristic.

        :param central: the central to notify or indicate to with the new data
        :param data: the data to 'send' to the central by setting the value of this characteristic to and
            notifying only that central
        :return: None
        """
        if not self.notifying:
            raise RuntimeWarning(
                "No central has indicated they want notifications on this characteristic, a central "
                "must subscribe before notifying/indicating"
            )

        if self.application is None or self.application.gatt_manager_interface is None:
            raise RuntimeError(
                "Unable to notify central of change without a bound application"
            )

        try:
            await self.application.gatt_manager_interface.call_notify_characteristic_changed(
                self.application.path,
                central.dbus_path,
                self.path,
                data,
            )
        except Exception:
            logger.exception(
                f"Exception caught when trying to notify {central}, are you sure the central is setup"
                "to notify on the characteristic?"
            )

    async def broadcast(self, data: Union[bytes, str]) -> None:
        """Broadcast characteristic's new value to every subscribed central

        :param data: the data to notify the centrals on
        """
        # Convert to bytes if it is a string
        if isinstance(data, str):
            data = data.encode("utf8")

        self.value = data

    @property
    def path(self) -> str:
        """Path property, raises an exception if not properly defined"""
        if self._path is None or not isinstance(self._path, str):
            raise RuntimeError(
                "Attempting to fetch path of an unset characteristic, has it been added correctly?"
            )
        return self._path
