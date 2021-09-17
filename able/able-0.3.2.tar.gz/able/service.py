#    Copyright (c)  2021  Allthenticate
"""
Abstraction of the ABleService that all backend services will inherit
"""

# Native modules
import uuid
from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from able.characteristic import ABleCharacteristic


class ABleService:
    """
    This is an abstract class for the Services that each platform backend defines. This class should never be used
    directly; instead, when the `ABleService` is imported from `able`, the appropriate subclass will be fetched
    based on what platform is being used.

    :param service_uuid: the uuid of the service.
    :ivar uuid: the uuid of the service
    :ivar characteristics:  a dictionary of uuid string - characteristic pairs, this is used to fetch a characteristic
        from a service if a reference to the characteristic is lost in your program.
    """

    def __init__(self, service_uuid: Union[str, uuid.UUID], **kwargs):
        """Initializes the able service"""

        # Define members used across all ABleServices
        self.uuid = str(service_uuid)
        self.characteristics: Dict[str, "ABleCharacteristic"] = {}

        # Work as a mixin
        super().__init__(**kwargs)  # type: ignore
