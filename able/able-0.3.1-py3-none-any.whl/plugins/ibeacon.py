# Copyright (c) 2021 Allthenticate
"""
This module contains the implementation of iBeacons, allowing users to send advertising packets using the iBeacon
format.
"""

# Native modules
import uuid
from typing import List, Optional, Union

# ABle Modules
from able.advertisement import ABleAdvertisement


def check_list(arr: List[bytes]) -> bool:
    """
    Utility function to make sure an object is a list of bytes
    """
    for elem in arr:
        # Check if elem is bytes
        if not isinstance(elem, bytes):
            return False
        # Check that elem is only 1 byte
        if len(elem) != 1:
            return False

    return len(arr) != 0


def validate_args(
    device_uuid: Union[str, uuid.UUID],
    major: List[bytes],
    minor: List[bytes],
    tx_power: List[bytes],
) -> Optional[bool]:
    """
    Utility function that validates the iBeacon data to make sure they conform to the iBeacon protocol
    """
    # Handle type checking
    if not isinstance(device_uuid, (str, uuid.UUID)):
        raise TypeError(f"Expected {device_uuid} to be of type string or UUID")

    if not check_list(major):
        raise TypeError(
            f"Expected {major} to be of a list of bytes (8-bits per byte element)"
        )

    if not check_list(minor):
        raise TypeError(
            f"Expected {major} to be of a list of bytes (8-bits per byte element)"
        )

    if not check_list(tx_power):
        raise TypeError(
            f"Expected {major} to be of a list of bytes (8-bits per byte element)"
        )

    # Handle length checking
    try:
        uuid.UUID(str(device_uuid))
    except ValueError as error:
        raise ValueError(f"Expected {device_uuid} to be a 16 byte UUID") from error

    if len(major) != 2:
        print(len(major))
        raise ValueError(f"Expected {major} to have length of 2 bytes")

    if len(minor) != 2:
        raise ValueError(f"Expected {minor} to have length of 2 bytes")

    if len(tx_power) != 1:
        raise ValueError(f"Expected {tx_power} to have length of 1 byte")

    return True


class ABleiBeacon(ABleAdvertisement):
    """
    Platform agnostic iBeacon class that creates an advertisement using Apple's iBeacon format
    Reference: https://en.wikipedia.org/wiki/IBeacon

    :param local_name: The name you wish to include within the advertisement packet as the local name
    :type local_name: str
    :param device_uuid: The uuid that you want to broadcast in the iBeacon
    :type device_uuid: Union[str, uuid.UUID]
    :param major: User-defined value to send in iBeacon data
    :type major: List[bytes]
    :param minor: User-defined value to send in iBeacon data
    :type minor: List[bytes]
    :param tx_power: User-defined value to send in iBeacon data
    :type tx_power: List[bytes]
    """

    def __init__(
        self,
        local_name: str,
        device_uuid: Union[str, uuid.UUID],
        major: List[bytes],
        minor: List[bytes],
        tx_power: List[bytes],
    ):
        """
        Initializes the iBeacon object and adds the data to the advertisement's manufacturing data
        """
        try:
            validate_args(device_uuid, major, minor, tx_power)
        except Exception as e:
            raise ValueError("Invalid parameters for initializing an iBeacon") from e

        super().__init__(local_name=local_name)

        # Constant values necessary for iBeacon
        self.company_id = 0x004C
        self.beacon_type = [b"\x02", b"\x15"]

        # User-defined values
        self.uuid = device_uuid
        self.major = major
        self.minor = minor
        self.tx_power = tx_power

        # Add iBeacon data to manufacturer data
        self._add_to_manufacturer_data()

    def _add_to_manufacturer_data(self) -> None:
        """
        Preps the iBeacon data and adds it to manufacturer data
        """
        # Convert uuid to bytes
        if isinstance(self.uuid, str):
            self.uuid = uuid.UUID(self.uuid)

        uuid_bytes = self.uuid.bytes
        uuid_arr = [uuid_bytes[i : i + 1] for i in range(len(uuid_bytes))]
        manu_data = b"".join(
            self.beacon_type + uuid_arr + self.major + self.minor + self.tx_power
        )

        self.add_manufacturer_data(self.company_id, manu_data)
