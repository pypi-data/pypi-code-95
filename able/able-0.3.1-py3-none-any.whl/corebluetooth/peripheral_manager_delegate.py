"""
PyObjC object of CBPeripheralManagerDelegate

API reference:
https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate
"""
# pylint: skip-file

# Native libraries
import asyncio
import logging
import threading
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set

import objc
from CoreBluetooth import (
    CBManagerStatePoweredOff,
    CBManagerStatePoweredOn,
    CBManagerStateResetting,
    CBManagerStateUnauthorized,
    CBManagerStateUnknown,
    CBManagerStateUnsupported,
)
from Foundation import (
    CBATTRequest,
    CBCentral,
    CBCharacteristic,
    CBMutableService,
    CBPeripheralManager,
    CBService,
    NSError,
    NSObject,
)
from libdispatch import DISPATCH_QUEUE_SERIAL, dispatch_queue_create

from able.corebluetooth.error import CBATTError

# Able Dependencies
from able.utils import DeviceCallbackData

if TYPE_CHECKING:
    from able.advertisement import ABleAdvertisement
    from able.central import ABleCentral
    from able.characteristic import ABleCharacteristic
    from able.corebluetooth.application import CBApplication

# Setup logging
logger = logging.getLogger(name=__name__)


class PeripheralManagerDelegate(NSObject):  # pylint: disable=invalid-name
    """Handles all the direct calls to the CBPeripheralManager"""

    CBPeripheralManagerDelegate = objc.protocolNamed("CBPeripheralManagerDelegate")
    ___pyobjc_protocols__ = [CBPeripheralManagerDelegate]

    async def setup(self) -> None:
        """
        Setup the CoreBluetooth peripheral manager

        :return: None
        """

        self = objc.super(  # pylint: disable=self-cls-assignment
            PeripheralManagerDelegate, self
        ).init()
        self.event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.peripheral_manager: CBPeripheralManager = (
            CBPeripheralManager.alloc().initWithDelegate_queue_(
                self,
                dispatch_queue_create(b"bleak.corebluetooth", DISPATCH_QUEUE_SERIAL),
            )
        )

        self._callbacks: Dict[str, Callable] = {}

        # Events
        self._powered_on_event: threading.Event = threading.Event()
        self._advertisement_started_event: asyncio.Event = asyncio.Event()
        self._services_added_events: Dict[str, asyncio.Event] = {}

        # Wait for bluetooth module to be powered on
        self._powered_on_event.wait()

        self._central_subscriptions = {}

        if not self.compliant():
            logger.warning("PeripheralManagerDelegate is not compliant")

    @objc.python_method
    def assign_app(self, app: "CBApplication") -> None:
        """Method to assign the CBApplication to instances of this class"""
        self._app = app

    def compliant(self) -> bool:
        """
        Determines whether the class adheres to the CBPeripheralManagerDelegate
        protocol
        Returns
        -------
        bool
            Whether the class is compliant with the CBPeripheralManagerDelegate
            Protocol
        """
        return PeripheralManagerDelegate.pyobjc_classMethods.conformsToProtocol_(
            self.CBPeripheralManagerDelegate
        )

    def is_connected(self) -> bool:
        """
        Determin whether any centrals have subscribed
        Returns
        -------
        bool
            True if other devices have subscribed to services
        """

        n_subscriptions = len(self._central_subscriptions)
        return n_subscriptions > 0

    def peripheralManagerDidUpdateState_(
        self, peripheral_manager: CBPeripheralManager
    ):  # pylint: disable=invalid-name
        """CB callback"""
        if peripheral_manager.state() == CBManagerStateUnknown:
            logger.debug("Cannot detect bluetooth device")
        elif peripheral_manager.state() == CBManagerStateResetting:
            logger.debug("Bluetooth is resetting")
        elif peripheral_manager.state() == CBManagerStateUnsupported:
            logger.debug("Bluetooth is unsupported")
        elif peripheral_manager.state() == CBManagerStateUnauthorized:
            logger.debug("Bluetooth is unauthorized")
        elif peripheral_manager.state() == CBManagerStatePoweredOff:
            logger.debug("Bluetooth powered off")
        elif peripheral_manager.state() == CBManagerStatePoweredOn:
            logger.debug("Bluetooth powered on")

        if peripheral_manager.state() == CBManagerStatePoweredOn:
            self._powered_on_event.set()
        else:
            self._powered_on_event.clear()
            self._advertisement_started_event.clear()

    def peripheralManager_willRestoreState_(  # pylint: disable=invalid-name,no-self-use
        self,
        peripheral: CBPeripheralManager,  # pylint: disable=unused-argument
        d: dict,
    ):
        """CB callback"""
        logger.debug("PeripheralManager restoring state: {}".format(d))

    ###############################
    # ADVERTISEMENT RELATED
    ###############################

    async def startAdvertising_(  # pylint: disable=invalid-name
        self,
        advertisement_data: "ABleAdvertisement",
        timeout: float = 2.0,
    ):
        """
        Begin Advertising on the server
        Parameters
        ----------
        advertisement_data : Dict[str, Any]
            Dictionary of additional data to advertise. See Apple Documentation
            for more info
        timeout : float
            How long to wait before throwing an error if advertising doesn't
            start
        """

        self.peripheral_manager.startAdvertising_(advertisement_data)

        await asyncio.wait_for(self._advertisement_started_event.wait(), timeout)

        logger.debug(
            "Advertising started with the following data: {}".format(advertisement_data)
        )

    def is_advertising(self) -> bool:
        """
        Determin whether the server is advertising
        Returns
        -------
        bool
            True if advertising
        """
        return self.peripheral_manager.isAdvertising()

    def stopAdvertising(self):  # pylint: disable=invalid-name
        """
        Stop Advertising
        """
        self.peripheral_manager.stopAdvertising()

    @objc.python_method
    def peripheralManagerDidStartAdvertising_error(  # pylint: disable=invalid-name
        self, peripheral_manager: CBPeripheralManager, error: NSError
    ):
        """CB callback"""
        if error:
            raise Exception("Failed to start advertising: {}".format(error))

        logger.debug("Peripheral manager did start advertising")
        self._advertisement_started_event.set()

    def peripheralManagerDidStartAdvertising_error_(  # pylint: disable=invalid-name
        self, peripheral_manager: CBPeripheralManager, error: NSError
    ):
        """CB callback"""
        logger.debug("Received DidStartAdvertising Message")
        self.event_loop.call_soon_threadsafe(
            self.peripheralManagerDidStartAdvertising_error, peripheral_manager, error
        )

    ###############################
    # SERVICE RELATED
    ###############################

    @objc.python_method
    async def addService(  # pylint: disable=invalid-name
        self, service: CBMutableService
    ):  # pylint: disable=invalid-name
        """
        Add a service to the peripheral

        Parameters
        ----------
        service : CBMutableService
            The service to be added to the server
        """
        service_uuid: str = service.UUID().UUIDString()
        self._services_added_events[service_uuid] = asyncio.Event()

        self.peripheral_manager.addService_(service)

        await self._services_added_events[service_uuid].wait()

    @objc.python_method
    def peripheralManager_didAddService_error(  # pylint: disable=invalid-name
        self,
        peripheral_manager: CBPeripheralManager,
        service: CBService,
        error: NSError,
    ):
        """CB callback"""
        uuid: str = service.UUID().UUIDString()
        if error:
            raise Exception("Failed to add service {}: {}".format(uuid, error))

        logger.debug("Peripheral manager did add service: {}".format(uuid))
        logger.debug(
            "service added had characteristics: {}".format(service.characteristics())
        )
        self._services_added_events[uuid].set()

    def peripheralManager_didAddService_error_(  # pylint: disable=invalid-name
        self,
        peripheral_manager: CBPeripheralManager,
        service: CBService,
        error: NSError,
    ):
        """CB callback"""
        self.event_loop.call_soon_threadsafe(
            self.peripheralManager_didAddService_error,
            peripheral_manager,
            service,
            error,
        )

    ###############################
    # CHARACTERISTIC RELATED
    ###############################

    def peripheralManager_central_didSubscribeToCharacteristic_(  # pylint: disable=invalid-name
        self,
        peripheral_manager: CBPeripheralManager,
        central: CBCentral,
        characteristic: CBCharacteristic,
    ):
        """CB callback"""
        central_uuid: str = central.identifier().UUIDString()
        char_uuid: str = characteristic.UUID().UUIDString()
        logger.debug(
            "Central Device: {} is subscribing to characteristic {}".format(
                central_uuid, char_uuid
            )
        )

        # Mark the characteristic as notifying
        char = self._get_char_from_uuid(char_uuid)
        if char is not None:
            char.client_subscribed.set()
        else:
            logger.debug(
                "Could not find characteristic that central subscribed to. Something bad must have happened!"
            )
            return

        # Check if this central is a new connection
        if central_uuid in self._app.connected_centrals:
            logger.debug(f"Central Device {central_uuid} is already connected")
            # Add the char UUID to central's char subscriptions
            central = self._app.connected_centrals[central_uuid]
            central.char_subscriptions.append(char_uuid)
        else:
            # Call connect callback in application
            device_data = DeviceCallbackData(central_uuid, char_uuid=char_uuid)
            self.event_loop.call_soon_threadsafe(
                self._app.connect_callback, central, device_data
            )

    def peripheralManager_central_didUnsubscribeFromCharacteristic_(  # pylint: disable=invalid-name
        self,
        peripheral_manager: CBPeripheralManager,
        central: CBCentral,
        characteristic: CBCharacteristic,
    ):
        """CB callback"""
        central_uuid: str = central.identifier().UUIDString()
        char_uuid: str = characteristic.UUID().UUIDString()
        logger.debug(
            "Central device {} is unsubscribing from characteristic {}".format(
                central_uuid, char_uuid
            )
        )

        # Mark the characteristic as NOT notifying
        char: "ABleCharacteristic" = self._get_char_from_uuid(char_uuid)
        if char is not None:
            char.client_subscribed.clear()
        else:
            logger.debug(
                "Could not find characteristic that central unsubscribed from. Something bad must have happened!"
            )
            return

        # Get central object
        central: "ABleCentral" = self._app.connected_centrals[central_uuid]

        # Remove char from subscriptions list
        central.char_subscriptions.remove(char_uuid)

        # Check if central is not subscribed to any chars, if so call disconnect callback
        if not central.char_subscriptions:
            device_data = DeviceCallbackData(central_uuid, char_uuid=char_uuid)
            self.event_loop.call_soon_threadsafe(
                self._app.disconnect_callback, device_data
            )

    def peripheralManagerIsReadyToUpdateSubscribers_(  # pylint: disable=invalid-name
        self, peripheral_manager: CBPeripheralManager
    ):
        """CB callback"""
        logger.debug("Peripheral is ready to update subscribers")

    def peripheralManager_didReceiveWriteRequests_(  # pylint: disable=invalid-name
        self, peripheral_manager: CBPeripheralManager, requests: List[CBATTRequest]
    ):
        """CB callback"""
        logger.debug("Receving write requests...")
        for request in requests:
            central_uuid: CBCentral = request.central().identifier().UUIDString()
            char_uuid: CBCharacteristic = request.characteristic().UUID().UUIDString()
            value: bytearray = request.value()

            logger.debug(f"Value received: {value}")

            able_char: "ABleCharacteristic" = self._get_char_from_uuid(char_uuid)
            self.event_loop.call_soon_threadsafe(
                able_char.set_value, value, central_uuid
            )

        peripheral_manager.respondToRequest_withResult_(
            requests[0], CBATTError.Success.value
        )

    def peripheralManager_didReceiveReadRequest_(  # pylint: disable=invalid-name
        self, peripheral_manager: CBPeripheralManager, request: CBATTRequest
    ):
        """CB callback"""
        logger.debug(
            "Received read request from {} for characteristic {}".format(
                request.central().identifier().UUIDString(),
                request.characteristic().UUID().UUIDString(),
            )
        )
        request.setValue_(request.characteristic().value())
        logger.debug(f"Reading {request.characteristic().value()}")
        peripheral_manager.respondToRequest_withResult_(
            request, CBATTError.Success.value
        )

    @objc.python_method
    def _get_char_from_uuid(self, char_uuid: str) -> Optional["ABleCharacteristic"]:
        for service in self._app.services:
            try:
                return service.characteristics[char_uuid.lower()]
            except Exception:
                continue
        return None
