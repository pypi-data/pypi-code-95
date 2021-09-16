#    Copyright (c)  2021  Allthenticate
"""
For reference of the implementation of this Gatt service abstraction, see:
https://gitlab.com/allthenticate/dependencies/bluez/-/blob/master/doc/gatt-api.txt
https://dbus.freedesktop.org/doc/dbus-tutorial.html
"""

# Native libraries
import logging
import uuid
from typing import TYPE_CHECKING, Dict, Optional

# Dependencies
from dbus_next.constants import PropertyAccess
from dbus_next.service import ServiceInterface, dbus_property

# Able Dependencies
from able.bluezdbus import BluezServiceInterfaces

# Setup logging
from able.service import ABleService

logger = logging.getLogger(name=__name__)

if TYPE_CHECKING:
    from able.characteristic import ABleCharacteristic


class BluezService(ABleService, ServiceInterface):
    """
    Class implementation of a BLE GATT Service using Dbus-Next. This class inherits from the `ABleService` so that
    it shares the same params for its constructor and supports the same capabilities as the services on other
    platforms. It also inherits from `ServiceInterface` so that this class can be exported on the DBus so that
    Bluez is able to get a proxy for this with the "org.bluez.GattService1" interface.

    :param service_uuid: the uuid for this service
    :param is_primary: whether or not this is a primary service, secondary services are rarely used as they
        are intended to be used in other services, defaults to True
    :ivar characteristics: a dictionary of uuid string - characteristic pairs, this is used to fetch a characteristic
        from a service if a reference to the characteristic is lost in your program.
    """

    def __init__(self, service_uuid: uuid.UUID, is_primary: bool = True):
        """Initialize the BluezService"""
        super().__init__(
            service_uuid, name=BluezServiceInterfaces.GATT_SERVICE_INTERFACE.value
        )

        # DBus values
        self.primary = is_primary
        self._path: Optional[str] = None

        # Additional members
        self.characteristics: Dict[str, "ABleCharacteristic"] = {}

    def __str__(self):
        return f"BluezLEService [{self.uuid}]"

    @dbus_property(access=PropertyAccess.READ, name="UUID")
    def _uuid(self) -> "s":  # type: ignore
        """
        Read only property for the bluez service to get the uuid of this gatt service interface.

        :return: 128-bit service UUID.
        """
        return str(self.uuid)

    @dbus_property(access=PropertyAccess.READ, name="Primary")
    def _primary(self) -> "b":  # type: ignore
        """
        Read only property for the bluez service to get whether or not this service is the primary service
        for the application.

        :return: Indicates whether or not this GATT service is a primary service. If false, the service is secondary.
        """
        return self.primary

    @property
    def path(self) -> str:
        """Path property, raises an exception if not properly defined"""
        if self._path is None:
            raise RuntimeError(
                "Attempting to fetch path of an unset service, has it been added correctly?"
            )
        return self._path
