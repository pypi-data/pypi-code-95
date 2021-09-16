"""
Implementation of a CoreBluetooth BLE advertisement using pyobjc as the interface
"""

# Native libraries
import logging
import uuid
from typing import Union

# Setup logging
logger = logging.getLogger(name=__name__)


class CBLEAdvertisement:
    """
    Simple class wrapper of the CoreBluetooth advertisementData dictionary
    For more information see:
    https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager/1393252-startadvertising

    :param local_name: The name you wish to include within advertisement packets as the local name, defaults to `BLE
        Peripheral`
    :type local_name: str
    """

    def __init__(self, advert_wrapper, local_name, *args, **kwargs):
        """Constructor for the CBLEAdvertisement"""

        # Advertisement values
        self.local_name = local_name if local_name is not None else "BLE Peripheral"
        self.service_uuids = []

        # Wrapper class, this is the able advertisement that owns this advert
        self.parent = advert_wrapper
        logger.warning(
            f"Use of args: {args} and {kwargs} not supported on macos backend"
        )

    def __str__(self):
        return f"CBLEAdvertisement [{self.local_name}, {self.service_uuids}"

    def __repr__(self):
        return str(self)

    def add_service_uuid(self, service_uuid: Union[str, uuid.UUID]) -> None:
        """
        Adds a service uuid to the advertisement object.

        :param service_uuid: What service uuid should be added to this advertisement
        :type service_uuid: Union[str, uuid.UUID]
        :return: None
        """
        if str(service_uuid) not in self.service_uuids:
            self.service_uuids.append(str(service_uuid))

    def add_service_data(
        self, service_uuid: Union[str, uuid.UUID], service_data: Union[str, bytes]
    ) -> None:
        """Not implemented because Core Bluetooth does not support this functionality. See:
        https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager/1393252-startadvertising"""
        raise NotImplementedError(
            "CoreBluetooth does not support adding service data to advertisements"
        )

    async def update_service_data(
        self, service_uuid: Union[str, uuid.UUID], service_data: Union[str, bytes]
    ) -> None:
        """Not implemented because Core Bluetooth does not support this functionality. See:
        https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager/1393252-startadvertising"""
        raise NotImplementedError(
            "CoreBluetooth does not support adding service data to advertisements"
        )

    def add_manufacturer_data(
        self, manufacturer_id: int, manufacturer_data: Union[str, bytes]
    ):
        """Not implemented because Core Bluetooth does not support this functionality. See:
        https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager/1393252-startadvertising"""
        raise NotImplementedError(
            "CoreBluetooth does not support adding manufacturer data to advertisements"
        )
