#    Copyright (c)  2021  Allthenticate
"""
Implementation of a BluezDbus BLE advertisement using dbus_next as the interface with Bluez over the dbus system bus.
"""

# Native libraries
import logging
import uuid
from typing import Union

# Dependencies
from dbus_next import Variant
from dbus_next.constants import PropertyAccess
from dbus_next.service import ServiceInterface, dbus_property, method

# Able Dependencies
from able.bluezdbus import AdvertisementType, BluezServiceInterfaces

# Setup logging
logger = logging.getLogger(name=__name__)


class BluezLEAdvertisement(ServiceInterface):
    """
    Class implementation of the BLE Advertisement Service through Dbus-Next, this is specific to the Linux platform and
    serves as the low level handler for individual advertisements.

    Note that right now we have not implemented a check for the advertisement's length so if you see errors in trying to
    add an advertisement, try removing some fields and try again, you may be over the max advertising length for your
    hardware.

    Note that the advertisement will also try to be restored if it is detected that the advertisement was released,
    triggering the application that holds it to refresh the advertisement in an attempt to recover it.

    :param local_name: The name you wish to include within advertisement packets as the local name, defaults to `BLE
        Peripheral`
    :type local_name: str
    :param advertisement_type: What type of advertisement this is, see `AdvertisementType` for the available types.
    :type advertisement_type: `AdvertisementType`, optional
    """

    def __init__(
        self,
        advert_wrapper,
        local_name="BLE Peripheral",
        advertisement_type=AdvertisementType.PERIPHERAL,
    ):
        """Constructor for the BluezLEAdvertisement"""
        # Call the super init with the type of interface
        super().__init__(name=BluezServiceInterfaces.ADVERTISEMENT_INTERFACE.value)

        # Advertisement values
        self.local_name = local_name
        self.ad_type = advertisement_type.value
        self.service_uuids = []
        self.manufacturer_data = {}
        self.service_data = {}

        # Note these are not available on every platform, see what the log of the supported capabilities are
        self.min_interval = 20
        self.max_interval = 20
        self.tx_power = 20
        self.appearance = 0x80  # default to generic computer

        # Dbus values
        self.application = None
        self.path = None

        # Wrapper class, this is the able advertisement that owns this advert
        self.parent = advert_wrapper

    def __str__(self):
        return f"BluezLEAdvertisement [{self.local_name}, {self.service_uuids}, {self.manufacturer_data}]"

    def __repr__(self):
        return str(self)

    def add_service_uuid(self, service_uuid: Union[str, uuid.UUID]) -> None:
        """
        Adds a service uuid to the advertisement object. Must follow the bluez spec for a service uuid
        otherwise bluez will reject the advertisement.

        :param service_uuid: What service uuid should be added to this advertisement.
        :type service_uuid: Union[str, uuid.UUID]
        :return: None
        """
        if str(service_uuid) not in self.service_uuids:
            self.service_uuids.append(str(service_uuid))

    def add_service_data(
        self, service_uuid: Union[str, uuid.UUID], service_data: Union[str, bytes]
    ) -> None:
        """
        Updates the service data of the advertisement to include the specified service data. Refer to the
        reference doc above for the limitations on service data.

        :raises ValueError: Will raise a value error if the service_uuid param does not correspond to a service
            uuid that this advertisement has.

        :param service_uuid: The uuid of the service to add the service data to, this must be a service uuid
            you have already added to the advertisement.
        :type service_uuid: Union[str, uuid.UUID]
        :param service_data: The service data to include in the advertisement under the service uuid.
        :type service_data: Union[str, bytes]
        :return: None
        """
        if str(service_uuid) not in self.service_uuids:
            raise ValueError(
                "Invalid service UUID provided, verify the service uuid was added to the advertisement"
            )

        if self.service_data.get(str(service_uuid)):
            logger.warning("Removing old service data from advertisement!")

        if isinstance(service_data, str):
            self.service_data[str(service_uuid)] = Variant(
                "ay", bytes(service_data.encode())
            )
        if isinstance(service_data, bytes):
            self.service_data[str(service_uuid)] = Variant("ay", service_data)

    async def update_service_data(
        self, service_uuid: Union[str, uuid.UUID], service_data: Union[str, bytes]
    ) -> None:
        """
        Update previously set service data with new data and refresh the advertisement using the bound application. This
        can be called after the `ABlePeripheralServer` that owns this advertisement has started advertising.

        :raises RuntimeError: Will raise an exception if this advertisement has not yet been added to an application,
            this is required for refreshing the service data.

        :param service_uuid: the uuid of the service whose service data you are updating.
        :type service_uuid: Union[str, uuid.UUID]
        :param service_data:  the service data to overwrite the previous service data with.
        :type service_data: Union[str, bytes]
        :return: None
        :rtype: None
        """
        if self.application is None:
            raise RuntimeError(
                "Tried to update service data without adding the advertisement to a running"
                "application, this will have no effect."
            )

        if service_uuid not in self.service_data:
            raise ValueError(
                "Invalid service UUID provided, there is no current service data"
            )

        if isinstance(service_data, str):
            self.service_data[service_uuid] = Variant(
                "ay", bytes(service_data.encode())
            )
        if isinstance(service_data, bytes):
            self.service_data[service_uuid] = Variant("ay", service_data)

        # Refresh the advertisement using the bound application
        await self.application.refresh_advertisement(advertisement=self.parent)

    def add_manufacturer_data(
        self, manufacturer_id: int, manufacturer_data: Union[str, bytes]
    ):
        """
        Updates the manufacturer data of the advertisement to include the specified manufacturer data. Refer to the
        reference doc above for the limitations on manufacturer data.

        TODO(Bernie, Ori): Add limitations for what the manufacturer data can be

        :param manufacturer_id: the id of the manufacturer to add the manufacturer data to, see the Bluetooth
            Special Interest groups website for what manufacturer id's are valid to be used in your use case.
        :type manufacturer_id: int
        :param manufacturer_data: the manufacturer data to add
        :type manufacturer_data: Union[str, bytes]
        :return: None
        :rtype: None
        """
        if self.manufacturer_data.get(manufacturer_id):
            logger.warning("Removing old manufacturer data from advertisement!")

        self.manufacturer_data[manufacturer_id] = Variant(
            "ay",
            bytes(
                manufacturer_data.encode()
                if isinstance(manufacturer_data, str)
                else manufacturer_data
            ),
        )

    @dbus_property(access=PropertyAccess.READ, name="Type")
    def _type(self) -> "s":  # type: ignore
        """
        Read only Dbus property to read the type of the advertisement.

        :return:  Determines the type of advertising packet requested. Possible values: "broadcast" or "peripheral"
        :rtype: str
        """
        return self.ad_type

    @dbus_property(access=PropertyAccess.READ, name="ServiceUUIDs")
    def _service_uuids(self) -> "as":  # type: ignore
        """
        Read only Dbus property to read the service uuids of the advertisement.

        :return:  List of UUIDs to include in the "Service UUID" field of
                        the Advertising Data.
        :rtype: list(str)
        """
        return self.service_uuids

    @dbus_property(access=PropertyAccess.READ, name="ServiceData")
    def _service_data(self) -> "a{sv}":  # type: ignore
        """
        Read only Dbus property to read the service data of the advertisement.

        :return: Service Data elements to include. The keys are the
                        UUID to associate with the data.
        :rtype: A dbus dictionary represnted by an array with strings as keys and variant entries which are
            arrays of bytes.
        """
        return self.service_data

    @dbus_property(access=PropertyAccess.READ, name="LocalName")
    def _local_name(self) -> "s":  # type: ignore
        """
        Read only Dbus property to local name of the advertisement.

        :return:  Local name to be used in the advertising report. If the
                        string is too big to fit into the packet it will be
                        truncated.
        :rtype: str
        """
        return self.local_name

    @dbus_property(access=PropertyAccess.READ, name="ManufacturerData")
    def _manufacturer_data(self) -> "a{qv}":  # type: ignore
        """
        Read only Dbus property to read the manufacturer data of the advertisement.

        :return: Manufacturer Data fields to include in the Advertising Data.  Keys are the Manufacturer ID
                        to associate with the data.
        :rtype: A dbus dictionary represented by an array with strings as keys and variant entries which are
            arrays of bytes.
        """
        return self.manufacturer_data

    @dbus_property(access=PropertyAccess.READ, name="MaxInterval")
    def _max_interval(self) -> "u":  # type: ignore
        """
        Dbus property which returns the max advertising interval if the advertising manager allows it.

        :return: The max interval in ms
        :rtype: uint32
        """
        return self.max_interval

    @dbus_property(access=PropertyAccess.READ, name="MinInterval")
    def _min_interval(self) -> "u":  # type: ignore
        """
        Dbus property which returns the min advertising interval if the advertising manager allows it.

        :return: The min interval in ms
        :rtype: uint32
        """
        return self.min_interval

    @dbus_property(access=PropertyAccess.READ, name="Appearance", disabled=True)
    def _appearance(self) -> "q":  # type: ignore
        """
        Appearance to be used in the advertising report. Possible values: as found on GAP Service.

        :return: The uint mapping to the appearance
        :rtype: uint16
        """
        return self.appearance

    @dbus_property(access=PropertyAccess.READ, name="TxPower", disabled=True)
    def _tx_power(self) -> "n":  # type: ignore
        """
        Dbus property which returns the transmission power of this advertising set if the advertising manager allows it.

        :return: The dBm this should be transmitted at [-127 + 20]
        :rtype: int16
        """
        return self.tx_power

    @method(name="Release")
    def _release(self):
        """
        This method gets called when the service daemon removes the Advertisement. A client can use it to do cleanup
        tasks. There is no need to call UnregisterAdvertisement because when this method gets called it has already
        been unregistered.

        TODO(Ori): Why does this not get called when we restart bluetoothd? See notion for this bug.

        :return: None
        :rtype: None
        """
        logger.debug(f"{self} has been released by bluez...")

        # Set the error state in the application
        self.application.error_state = True
