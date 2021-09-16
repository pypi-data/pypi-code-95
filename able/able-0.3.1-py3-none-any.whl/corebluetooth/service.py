"""CoreBluetooth service in python"""

# Copyright (c) 2021 Allthenticate


import uuid
from typing import Union

from CoreBluetooth import CBUUID, CBMutableService  # type: ignore

from able.service import ABleService


class ABleCBService(ABleService):
    """
    Wrapper around the CoreBluetooth service (CBMutableService)

    :param service_uuid: the uuid for this service
    :param is_primary: whether or not this is a primary service, secondary services are rarely used as they
        are intended to be used in other services, defaults to True
    """

    def __init__(
        self, service_uuid: Union[uuid.UUID, str], is_primary: bool = True
    ) -> None:
        """Initialize the ABleCBService"""

        super().__init__(service_uuid)

        cb_service: CBMutableService = CBMutableService.alloc().initWithType_primary_(
            CBUUID.alloc().initWithString_(str(service_uuid)), is_primary
        )

        self.obj = cb_service
