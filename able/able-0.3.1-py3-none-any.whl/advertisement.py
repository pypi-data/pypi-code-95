# Copyright (c) 2021 Allthenticate
"""
This module contains the implementation of the ABleAdvertisement, the top level le_advertisement
class that relies on platform specific implementations but exposes key parts of the API that
is not platform specific.
"""

# Native modules
import logging
import uuid
from typing import Union

# ABle Modules
from able import LEAdvertisement

# Configure logging
logger = logging.getLogger(__name__)


class ABleAdvertisement:
    """
    A platform agnostic BLE le_advertisement class. This wrapper illustrates the platform specific
    le_advertisement implementations and utilizes the implementation of each backends specific le_advertisement
    in the `self.le_advertisement` member.

    Note that validation of inputs for member functions is handled in this class instead of having the validation
    duplicated on each backend, the only exception to this is platform specific restrictions.

    :param local_name: The name you wish to include within le_advertisement packets as the local name
    """

    def __init__(self, local_name: str, *args, **kwargs):
        """Initializes the mixin le_advertisement class"""
        self.local_name = local_name

        # Handle the platform specific le_advertisement object passing in any kwargs
        self.le_advertisement = LEAdvertisement(self, self.local_name, *args, **kwargs)

        logger.info(
            f"Initialized ABleAdvertisement using {type(self.le_advertisement)}"
        )

    def __str__(self):
        return f"ABleAdvertisement using the {type(self.le_advertisement)} advertising backend"

    def __repr__(self):
        return f"ABleAdvertisement({self.local_name})"

    def add_service_uuid(self, service_uuid: Union[str, uuid.UUID]) -> None:
        """
        Adds a service uuid to the le_advertisement. Please see the Bluetooth SIG's specification
        for service uuids and which uuids are assigned/reserved.

        :raises ValueError: if `service_uuid` is not of type str or uuid.UUID

        :param service_uuid: the service uuid to add to the le_advertisement
        :return: None
        """
        # Handle type checking
        if not isinstance(service_uuid, (str, uuid.UUID)):
            raise TypeError(f"Expected {service_uuid!r} to be a str or uuid.UUID")

        return self.le_advertisement.add_service_uuid(service_uuid)

    def add_service_data(
        self, service_uuid: Union[str, uuid.UUID], service_data: Union[str, bytes]
    ) -> None:
        """
        Adds service data for a service uuid within the le_advertisement. Note that the service uuid
        must be added before the service data can be added.

        :raises ValueError: if `service_uuid` is not of type str or uuid.UUID or if `service_data` is not
            of type str or bytes

        :param service_uuid: The uuid of the service to add the service data to, this must be a service uuid
            you have already added to the le_advertisement
        :param service_data: The service data to include in the le_advertisement under the service uuid
        :return: None
        """
        # Handle type checking
        if not isinstance(service_uuid, (str, uuid.UUID)):
            raise TypeError(f"Expected {service_uuid!r} to be a str or uuid.UUID")
        if not isinstance(service_data, (str, bytes)):
            raise TypeError(f"Expected {service_data!r} to be a str or bytes")

        return self.le_advertisement.add_service_data(service_uuid, service_data)

    async def update_service_data(
        self, service_uuid: Union[str, uuid.UUID], service_data: Union[str, bytes]
    ) -> None:
        """
        Update previously set service data with new data and refresh the le_advertisement using the bound
        application. This can be only called after the `ABlePeripheralServer` that owns this le_advertisement
        has started advertising.

        :raises ValueError: if `service_uuid` is not of type str or uuid.UUID or if `service_data` is not
            of type str or bytes

        :param service_uuid: the uuid of the service whose service data you are updating.
        :param service_data:  the service data to overwrite the previous service data with.
        :return: None
        """
        # Handle type checking
        if not isinstance(service_uuid, (str, uuid.UUID)):
            raise TypeError(f"Expected {service_uuid!r} to be a str or uuid.UUID")
        if not isinstance(service_data, (str, bytes)):
            raise TypeError(f"Expected {service_data!r} to be a str or bytes")

        return await self.le_advertisement.update_service_data(
            service_uuid, service_data
        )

    def add_manufacturer_data(
        self, manufacturer_id: int, manufacturer_data: Union[str, bytes]
    ) -> None:
        """
        Updates the manufacturer data of the le_advertisement to include the specified manufacturer data. Refer to the
        reference doc above for the limitations on manufacturer data.

        :raises ValueError: if `manufacturer_id` is not of type 16-bit unsigned int or `manufacturer_data` is not
            of type str or bytes

        :param manufacturer_id: the id of the manufacturer to add the manufacturer data to, see the Bluetooth
            Special Interest groups website for what manufacturer id's are valid to be used in your use case.
        :param manufacturer_data: the manufacturer data to add
        :return: None
        """
        # Handle type checking
        if not isinstance(manufacturer_id, int) or not 0 <= manufacturer_id <= 65535:
            raise TypeError(
                f"Expected {manufacturer_id!r} to be an unsigned 16-bit integer!"
            )
        if not isinstance(manufacturer_data, (str, bytes)):
            raise TypeError(f"Expected {manufacturer_data!r} to be a str or bytes")

        return self.le_advertisement.add_manufacturer_data(
            manufacturer_id, manufacturer_data
        )
