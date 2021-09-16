#    Copyright (c)  2021  Allthenticate
"""
For references of this implementation see of a bluezdbus application:

Advertising: https://gitlab.com/allthenticate/dependencies/bluez/-/blob/master/doc/advertising-api.txt
GATT: https://gitlab.com/allthenticate/dependencies/bluez/-/blob/master/doc/gatt-api.txt
DBUS: https://dbus.freedesktop.org/doc/dbus-specification.html
dbus-next: https://python-dbus-next.readthedocs.io/_/downloads/en/latest/pdf/
"""

# Native libraries
import asyncio
import logging
import re
import subprocess
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set

# Dependencies
from dbus_next import DBusError, Message, Variant
from dbus_next.aio import MessageBus, ProxyInterface, ProxyObject
from dbus_next.constants import BusType
from dbus_next.service import ServiceInterface

from able.bluezdbus import (
    BluezServiceInterfaces,
    DBusInterface,
    DbusServiceInterfaces,
    get_advertisement_object_path,
    get_characteristic_path,
    get_service_path,
)
from able.bluezdbus.advertisement import BluezLEAdvertisement
from able.bluezdbus.characteristic import BluezCharacteristic
from able.bluezdbus.service import BluezService
from able.bluezdbus.utils import add_match, remove_match

# Able Dependencies
from able.utils import DeviceCallbackData

if TYPE_CHECKING:
    from able.advertisement import ABleAdvertisement
    from able.central import ABleCentral
    from able.characteristic import ABleCharacteristic
    from able.service import ABleService

# Setup logging
logger = logging.getLogger(name=__name__)

BLUETOOTH_FIVE_HCI_VERSION = 0x9


def _check_support_for_always_advertising(adapter_path: str) -> bool:
    """
    Advertising while connected is only supported on adapters with HCI version ^5.0, this function uses
    hciconfig to check the version the adapter specified.

    :param adapter_path: the adapter path to check (eg. /org/bluez/hci0)
    :return: `True` if multiple
    """
    try:
        # Get the HCI version from hciconfig
        output = subprocess.run(
            ["hciconfig", "-a", adapter_path], stdout=subprocess.PIPE, check=True
        )

        # Find the version number using a re
        version_match = re.search(
            r"HCI Version:[^|\n]*\((.*)\)", output.stdout.decode()
        )

        if version_match is None:
            logger.warning("Unable to parse HCI version from hciconfig")
            return False

        version = int(version_match.group(1), 16)
        logger.debug(
            f"Detected HCI version is {version}, needs to be {BLUETOOTH_FIVE_HCI_VERSION} for "
            f"advertising while connected"
        )

        # Return if it is greater than or equal to bluetooth 5
        return version >= BLUETOOTH_FIVE_HCI_VERSION
    except Exception:
        logger.exception(
            "Unable to determine if always advertising is supported, defaulting to False"
        )
        return False


class BluezApplication(ServiceInterface):
    """
    The high level application that abstracts Dbus Calls

    :param name: the name that this application should request on the dbus
    :param auto_recover: if `True` will try to recover if bluez restarts, defaults to `False`
    :param adapter_path: what is the path to the hardware adapter, will be the first one discovered if not provided,
        eg. /org/bluez/hci0
    """

    def __init__(
        self, name: str, adapter_path: Optional[str] = None, auto_recover: bool = False
    ):
        """Initializer for the bluezdbus application"""
        super().__init__(BluezServiceInterfaces.GATT_MANAGER_INTERFACE.value)

        # Dbus related
        self.name = name
        self.path = "/"
        self._bus: Optional[MessageBus] = None
        self.gatt_manager_interface = None
        self.adapter_interface: Optional[ProxyInterface] = None
        self.proxy_objects: Dict[str, Dict[str, ProxyObject]] = {}
        self.match_rules: Set[str] = set()
        self.auto_recover = auto_recover
        self.error_state = False

        # Advertising related
        self.advertisements: Dict[int, "ABleAdvertisement"] = {}
        self.advertising_manager: Optional[ProxyInterface] = None
        self.adapter_path = adapter_path
        self.adapter_properties: Optional[ProxyInterface] = None
        self.supported_includes = None
        self.advertising_lock: Optional[asyncio.Lock] = None

        # Services related
        self.services: List[BluezService] = []

        # Params
        self.max_advertisements = 5
        self.advertising_capabilities: Dict[str, int] = {}
        self.always_advertising_supported = False

        # Connection related
        self.has_new_central = asyncio.Event()
        self.new_connection_queue: Set["ABleCentral"] = set()
        self.connected_centrals: Dict[str, "ABleCentral"] = {}
        self.user_connect_callback: Optional[Callable] = None
        self.user_disconnect_callback: Optional[Callable] = None

        # Communication related
        self.marked_characteristic: Optional[BluezCharacteristic] = None

    def __setattr__(self, key, value):
        self.__dict__[key] = value

        # If something is setting the error state, call recovery functions
        if key == "error_state" and value and self.auto_recover:
            logger.warning(
                "Error state declared by a module with auto recover set, attempting to recover"
            )
            try:
                for advertisement in self.advertisements.values():
                    asyncio.create_task(self.refresh_advertisement(advertisement))
                self.error_state = False
                logger.info("Recovered from error state!")
            except Exception:
                logger.exception("Recovery failed...")

    async def cleanup(self) -> None:
        """
        This function should be called when the program exits and will handle all cleanup similar to a
        destructor.

        TODO(Bernie): Debug handling here

        :return: None
        """

        if self.bus is not None:

            async def _cleanup():
                for rule in self.match_rules:
                    await remove_match(self.bus, match_rule=rule)

            asyncio.run(_cleanup())
            self.bus.disconnect()
        logger.info("BluezApplication cleanup completed. ")

    async def _get_proxy_object(self, bus_name: str, path: str) -> ProxyObject:
        """Gets a proxy object, the dbus equivalent is bus.get_object(bus_name, path)"""
        # Check if we already have this proxy stored
        if bus_name not in self.proxy_objects:
            self.proxy_objects[bus_name] = {}

        if path not in self.proxy_objects[bus_name]:
            self.proxy_objects[bus_name][path] = self.bus.get_proxy_object(
                bus_name, path, await self.bus.introspect(bus_name, path)
            )

        # Return the proxy object
        return self.proxy_objects[bus_name][path]

    async def get_proxy_interface(
        self, bus_name: DBusInterface, path: str, interface_name: DBusInterface
    ) -> ProxyInterface:
        """Gets a proxy interface using the _get_proxy_object method"""
        proxy_object = await self._get_proxy_object(bus_name.value, path)
        return proxy_object.get_interface(interface_name.value)

    async def setup(self) -> None:
        """
        Setup the application and get it on the dbus, this is a necessary function call to initialize the object.

        :return: None
        """
        # Get on the Dbus
        self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        self.bus.add_message_handler(self._dbus_message_parser)

        await self.bus.request_name(
            f"{BluezServiceInterfaces.BLUEZ_ORG.value}.{self.name}"
        )

        # Connect to bluez
        remote_object_manager = await self.get_proxy_interface(
            bus_name=BluezServiceInterfaces.BLUEZ_ORG,
            path="/",
            interface_name=DbusServiceInterfaces.OBJECT_MANAGER_INTERFACE,
        )

        # Find the path of an adapter with advertising capability
        if self.adapter_path is None:
            objects = await remote_object_manager.call_get_managed_objects()  # type: ignore
            for adapter, props in objects.items():
                if BluezServiceInterfaces.ADVERTISING_MANAGER_INTERFACE.value in props:
                    self.adapter_path = adapter
                    break

        # If no adapter is found, error out
        if self.adapter_path is None:
            raise RuntimeError("No adapter found, is a bluetooth adapter plugged in?")

        # Power the adapter
        logger.debug(self.adapter_path)
        self.adapter_properties = await self.get_proxy_interface(
            bus_name=BluezServiceInterfaces.BLUEZ_ORG,
            path=self.adapter_path,
            interface_name=DbusServiceInterfaces.PROPERTIES_INTERFACE,
        )
        await self.adapter_properties.call_set(  # type: ignore
            BluezServiceInterfaces.ADAPTER_INTERFACE.value,
            "Powered",
            Variant("b", True),
        )
        logger.debug(f"{self.adapter_path} is powered!")

        # Check if the adapter supports advertising while connected (ble v^5)
        self.always_advertising_supported = _check_support_for_always_advertising(
            self.adapter_path
        )
        if not self.always_advertising_supported:
            logger.warning(
                "HCI version is sub 5.0 which doesn't support advertising while connected always."
            )

        # Get the adapter interface, we need this for removing devices
        self.adapter_interface = await self.get_proxy_interface(
            bus_name=BluezServiceInterfaces.BLUEZ_ORG,
            path=self.adapter_path,
            interface_name=BluezServiceInterfaces.ADAPTER_INTERFACE,
        )

        # Find the advertisement manager and store it for later
        self.advertising_manager = await self.get_proxy_interface(
            bus_name=BluezServiceInterfaces.BLUEZ_ORG,
            path=self.adapter_path,
            interface_name=BluezServiceInterfaces.ADVERTISING_MANAGER_INTERFACE,
        )

        # Try to get the maximum number of advertisements we can use
        try:
            self.max_advertisements = (
                await self.advertising_manager.get_supported_instances()  # type: ignore
            )
            logger.info(f"Hardware supports {self.max_advertisements} advertisements.")
        except Exception:
            logger.exception(
                "Unable to get the number of supported instances from the adapter."
            )

        # Try to get the supported capabilities of advertising manager
        try:
            self.advertising_capabilities = (
                await self.advertising_manager.get_supported_capabilities()  # type: ignore
            )

            # Try to pull out variant values
            for key, value in self.advertising_capabilities.items():
                if isinstance(value, Variant):
                    self.advertising_capabilities[key] = value.value

            logger.info(
                f"Advertising manager supports: {self.advertising_capabilities}"
            )
        except Exception:
            logger.exception(
                "Unable to get supported capabilities of advertising manager."
            )

        # Try to get the params we can utilize
        try:
            self.supported_includes = (
                await self.advertising_manager.get_supported_includes()  # type: ignore
            )
            logger.info(
                f"Hardware supports {self.supported_includes} which can be controlled in software"
            )
        except Exception:
            logger.exception(
                "Unable to get the supported includes from the adapter interface."
            )

        logger.info(f"BluezApplication started with adapter: {self.adapter_path}")

        self.match_rules.add(
            "type=signal,interface=org.freedesktop.DBus.Properties,member=PropertiesChanged,"
            f"path_namespace={self.adapter_path}"
        )
        self.match_rules.add(
            "type=signal,interface=org.freedesktop.DBus.ObjectManager,member=InterfacesRemoved,"
            f"arg0path={self.adapter_path}/"
        )
        self.match_rules.add(
            "type=signal,interface=org.freedesktop.DBus.ObjectManager,member=InterfacesAdded,"
            f"arg0path={self.adapter_path}/"
        )

        for rule in self.match_rules:
            await add_match(self.bus, match_rule=rule)

        self.advertising_lock = asyncio.Lock()
        logger.debug("Setup complete!")

    async def add_advertisement(self, advertisement: "ABleAdvertisement") -> None:
        """Adds an le_advertisement object to the application"""

        # Fetch the bluez advert from the wrapper
        le_advertisement = advertisement.le_advertisement

        # Input validation
        if not isinstance(le_advertisement, BluezLEAdvertisement):
            raise TypeError(
                f"Advertisement error is the wrong type for this platform: {type(le_advertisement)}"
            )

        if le_advertisement in self.advertisements.values():
            raise ValueError("Attempting to add le_advertisement already added!")

        if len(self.advertisements) == self.max_advertisements:
            raise RuntimeError("Unable to add any more advertisements!")

        # Get the path we will place it on the dbus, we need to find the first index we aren't actively using
        valid_indices = list(
            set(range(self.max_advertisements)) - set(self.advertisements.keys())
        )

        advertisement_index = valid_indices[0]
        advertisement_path = get_advertisement_object_path(
            self.name, advertisement_index
        )

        # Export the object onto the system bus
        self.bus.export(advertisement_path, le_advertisement)

        # Add it to bluez
        try:
            await self.advertising_manager.call_register_advertisement(  # type: ignore
                advertisement_path, {}
            )
        except DBusError as e:
            raise RuntimeError(
                "Attempted to add an invalid le_advertisement, maybe it is too long or the params are invalid, try"
                "running the script again while watching $ sudo btmon"
            ) from e

        # Add this application to the le_advertisement
        le_advertisement.application = self

        # Add it to our tracker of advertisements
        self.advertisements[advertisement_index] = advertisement
        logger.debug(f"Advertisement added! ({advertisement_path})")

    async def remove_advertisement(self, advertisement: "ABleAdvertisement") -> None:
        """Removes an le_advertisement object from the application"""

        # Input validation
        if not isinstance(advertisement.le_advertisement, BluezLEAdvertisement):
            raise TypeError(
                f"Advertisement error is the wrong type for this platform: {type(advertisement.le_advertisement)}"
            )

        if advertisement not in self.advertisements.values():
            raise ValueError("Attempting remove le_advertisement not being advertised!")

        # Get the path we will place it on the dbus
        advertisement_index = None
        for index, active_adv in self.advertisements.items():
            if active_adv == advertisement:
                advertisement_index = index

        assert advertisement_index is not None, "This should be impossible..."
        advertisement_path = get_advertisement_object_path(
            self.name, advertisement_index
        )

        try:
            await self.advertising_manager.call_unregister_advertisement(  # type: ignore
                advertisement_path
            )
            del self.advertisements[advertisement_index]

            # Export the object onto the system bus
            self.bus.unexport(advertisement_path, advertisement.le_advertisement)
        except Exception:
            logger.exception(
                "Unable to remove le_advertisement! (this is okay during recovery)"
            )

        logger.debug(f"Advertisement removed ({advertisement_path})")

    def add_service(self, service: "ABleService") -> None:
        """
        Adds a bluez service to the application, this must be done before running start_application()

        :raises TypeError: if service is not of type BluezService
        :raises RuntimeError: if the service has already been added to the application

        :param service: the service to add to the bluez application
        :return: None
        """
        if not isinstance(service, BluezService):
            raise TypeError(
                f"The service that is trying to be added is the wrong type for this platform: {type(service)}"
            )

        # Double check it has not already been added
        if service in self.services:
            raise RuntimeError(f"Already added {service} to the application.")

        # Determine the path of the service and add it to the services list
        # pylint: disable=protected-access
        service._path = get_service_path(self.name, len(self.services) + 1)
        self.services.append(service)

        # Export this service as an object on the dbus
        self.bus.export(service.path, service)

    def add_characteristic(
        self,
        service: "ABleService",
        characteristic: "ABleCharacteristic",
        is_comms_char: bool = False,
    ) -> None:
        """
        Adds a characteristic to the application, this must done before running start_application()

        TODO(Bernie): What kind of validation should we do here?

        :param is_comms_char: if `True` the characteristic will become the comms characteristic, defaults to `False`
        :param service: the service which the characteristic will be added under
        :param characteristic: the characteristic you wish to add to the service
        :return: None
        """
        if not isinstance(service, BluezService):
            raise TypeError(
                "The service must be the of type BluezService to add to a Bluez application"
            )
        if not isinstance(characteristic, BluezCharacteristic):
            raise TypeError(
                "The characteristic must be of the type BluezCharacteristic to add to a Bluez application"
            )

        # Make sure there wasn't already a characteristic with that UUID
        if characteristic.uuid in service.characteristics.keys():
            raise ValueError(
                "Adding a characteristic with a UUID that matches another characteristic in the service!"
            )

        # Calculate the path of the characteristic
        characteristic._path = (  # pylint: disable=protected-access
            get_characteristic_path(service.path, len(service.characteristics) + 1)
        )

        # Add the characteristic to the service
        service.characteristics[characteristic.uuid] = characteristic

        # Link the characteristic to the service
        characteristic.service = service
        characteristic.application = self

        if is_comms_char:
            # Now handle marking updating by removing the old one and adding the new one
            if self.marked_characteristic is not None:
                logger.debug(
                    f"{self.marked_characteristic} is no longer marked for comms."
                )
                self.marked_characteristic.is_marked = False

            characteristic.is_marked = True
            self.marked_characteristic = characteristic
            logger.debug(f"{self.marked_characteristic} is now marked for comms")

        # Export it on the bus
        self.bus.export(characteristic.path, characteristic)

    def add_connect_callback(self, callback: Callable) -> None:
        """
        Adds a user-defined callback function to the application to be called after connecting to a central device.
        :param callback: the function to be called after a successful connection
        :return: None
        """
        self.user_connect_callback = callback

    def add_disconnect_callback(self, callback: Callable) -> None:
        """
        Adds a user-defined callback function to the application to be called after disconnecting from a central device.
        :param callback: the function to be called after a successful disconnect
        :return: None
        """
        self.user_disconnect_callback = callback

    async def start_interface(self):
        """
        Starts the GATT manager interface by registering it with the bluez service manager. Note that any
        services and their respective characteristics must be added before this is called.

        :return: None
        """
        # Check to see that at least one service was added, bluez will not allow willy nilly service-less advertising
        # https://github.com/luetzel/bluez/blob/aae6a2c4ce9963db110535647aa723b96561f6ac/src/gatt-database.c#L2452
        if len(self.services) == 0:
            raise RuntimeError(
                "You cannot start the interface on bluez without adding at least one service"
            )

        if self.gatt_manager_interface is None:
            self.gatt_manager_interface: ProxyInterface = (
                await self.get_proxy_interface(
                    BluezServiceInterfaces.BLUEZ_ORG,
                    self.adapter_path,
                    BluezServiceInterfaces.GATT_MANAGER_INTERFACE,
                )
            )

        # Try to unexport anything on the message bus
        self.bus.unexport(self.path)

        self.bus.export(self.path, self)
        await self.gatt_manager_interface.call_register_application(self.path, {})
        logger.debug("Registered application with the bluez service manager.")

    async def refresh_advertisement(self, advertisement: "ABleAdvertisement"):
        """Hack to try to update params by stopping and restarting the interface"""
        if not isinstance(self.advertising_lock, asyncio.Lock):
            raise RuntimeError(
                "Unable to refresh advertisement, has the setup method been ran?"
            )

        async with self.advertising_lock:
            await self.remove_advertisement(advertisement)
            await self.add_advertisement(advertisement)

    def _dbus_message_parser(self, message: Message) -> None:
        """
        Handler for all dbus messages that we have match rules for. We have two main routes and check them
        through either properties changed or interfaces added.

        TODO(Ori): Change the mac address parsing to use the parse_identifier_from_path function in utils.py

        :param message: The dbus message we caught.
        :return: None
        """
        try:
            if message.member == "PropertiesChanged":
                # Handle validation, we are expecting a list of length 3
                if not isinstance(message.body, list) or len(message.body) != 3:
                    return

                # The first element in the 3 long list needs to be org.bluez.Device1
                if message.body[0] != "org.bluez.Device1":
                    return

                # Make sure the message has a path
                if message.path is None:
                    return

                data: dict = message.body[1]
                object_path: str = message.path
                device_mac = object_path[
                    object_path.find("_") + 1 : object_path.rfind("_") + 3
                ]

                # Make sure that this is the connected properties changed signal
                if "Connected" not in data:
                    return

                if data["Connected"].value:
                    logger.info("Calling connected callback off of props changed...")
                    self.connect_callback(
                        DeviceCallbackData(devices_identifier=device_mac)
                    )
                else:
                    logger.info("Calling disconnect callback off of props changed...")
                    self.disconnect_callback(
                        DeviceCallbackData(devices_identifier=device_mac)
                    )

            elif message.member == "InterfacesAdded":
                # Handle validation, we expect a list of length 2
                if not isinstance(message.body, list) or len(message.body) != 2:
                    return

                # Make sure that a device path is the first element in the path
                if self.adapter_path not in message.body[0]:
                    return

                # Make sure this is the right interfaces added
                if "org.bluez.Device1" not in message.body[1]:
                    return

                # Make sure that this is a device with an address!
                if "Address" not in message.body[1]["org.bluez.Device1"]:
                    return

                # Make sure that it is connected and not a signal from a disconnected but cached device
                if (
                    "Connected" in message.body[1]["org.bluez.Device1"]
                    and not message.body[1]["org.bluez.Device1"]["Connected"].value
                ):
                    return

                # Parse out the path of the central
                central_mac = message.body[1]["org.bluez.Device1"]["Address"].value

                # Call the connect callback
                logger.info(
                    "Calling connected callback off of interfaces added signal..."
                )
                self.connect_callback(
                    DeviceCallbackData(devices_identifier=central_mac)
                )

        except Exception:
            logger.exception(
                "Unhandled exception when parsing dbus-next signal message..."
            )

    def connect_callback(self, callback_data: DeviceCallbackData) -> None:
        """
        Handler for the new connections being signalled from bluez. Verifies that the central was not already connected
        and is being stored in the connected_centrals dictionary (this would mean we lost state). Adds an entry to the
        new connection queue so that a peripheral server can accept the new connection. Adds a new ABleCentral to the
        connected centrals dictionary. Calls an optional user defined callback last.

        :param callback_data: data including the identifier required to create ABleCentral
        :return: None
        """
        from able.central import ABleCentral  # pylint: disable=import-outside-toplevel

        logger.info(f"New connection from {callback_data}")

        if callback_data.identifier in self.connected_centrals:
            raise RuntimeWarning(
                f"Received a double connection from {callback_data.identifier}, we missed a disconnect "
                "callback"
            )

        # Add to the NCQ
        new_central: "ABleCentral" = ABleCentral(
            application=self,
            identifier=callback_data.identifier,
            adapter_path=self.adapter_path,
        )
        self.new_connection_queue.add(new_central)
        self.connected_centrals[callback_data.identifier] = new_central

        # Add a receive queue for each characteristic
        for service in self.services:
            for char in service.characteristics.values():
                new_central.char_queues[hash(char)] = asyncio.Queue()
                logger.debug(
                    f"Queue was created for characteristic {char.uuid} on central {new_central}"
                )

        # Set the new connection event if it is not already set
        if not self.has_new_central.is_set():
            self.has_new_central.set()

        logger.debug(f"{self.new_connection_queue} | {self.connected_centrals}")

        if self.always_advertising_supported:
            for advert in self.advertisements.values():
                asyncio.create_task(self.refresh_advertisement(advert))

        if self.user_connect_callback:
            try:
                self.user_connect_callback(callback_data)
            except TypeError:
                logger.exception(
                    "User-defined connection callback is not able to be called with the argument given"
                )

    def disconnect_callback(self, callback_data: DeviceCallbackData) -> None:
        """
        Handler for disconnections being signalled by bluez. Updates the disconnected ABleCentral's state to be
        disconnected. Removes the central from the connected centrals dictionary (if it was there, it will not be
        present if the connection was established before the application was running) and the new connection queue
        if it is present. Calls an optional user defined callback last.

        :param callback_data: data regarding the central which disconnected
        :return: None
        """
        from able.central import ABleCentral  # pylint: disable=import-outside-toplevel

        logger.info(f"Disconnect from {callback_data}")

        # Make sure the central was already connected, if not it is okay
        if callback_data.identifier not in self.connected_centrals:
            logger.warning("A central disconnected which we did not know was connected")
            return

        # Get the central which disconnected the centrals state to disconnected
        disconnecting_central: ABleCentral = self.connected_centrals[
            callback_data.identifier
        ]
        disconnecting_central.disconnected_event.set()

        # Remove from the connected centrals dict and the NCQ
        self.new_connection_queue.discard(disconnecting_central)
        self.connected_centrals.pop(callback_data.identifier)

        # If we no longer have any connections, unset the event
        if len(self.new_connection_queue) == 0:
            logger.debug(
                "There are no more clients in the NCQ, clearing has_new_central event"
            )
            self.has_new_central.clear()

        logger.info(f"{self.new_connection_queue} | {self.connected_centrals}")

        if self.always_advertising_supported:
            for advert in self.advertisements.values():
                asyncio.create_task(self.refresh_advertisement(advert))

        if self.user_disconnect_callback:
            try:
                self.user_disconnect_callback(callback_data)
            except TypeError:
                logger.exception(
                    "User-defined disconnect callback is not able to be called with the argument given"
                )

    async def disconnect(self, central: "ABleCentral") -> None:
        """
        Call bluez to disconnect a connected central, this will not update the connected state of the central because
        the disconnect callback will handle that.

        # TODO(Bernie, Ori): Test the reliability of using remove_device vs disconnect

        :param central: The central object to force a disconnect.
        :return: None
        """
        logger.info(f"Disconnecting from central: {central.identifier}")

        try:
            # await self.adapter_interface.call_remove_device(central.dbus_path)
            device_interface = await self.get_proxy_interface(
                BluezServiceInterfaces.BLUEZ_ORG,
                central.dbus_path,
                BluezServiceInterfaces.DEVICE_INTERFACE,
            )

            await device_interface.call_disconnect()  # type: ignore
            logger.info(f"Disconnected from {central}...")
        except Exception:
            logger.exception(f"Unable to disconnect from {central.dbus_path}")

    @property
    def communication_characteristic(self) -> BluezCharacteristic:
        """Property which returns the marked comms characteristic or raises an exception"""
        if self.marked_characteristic is None:
            raise RuntimeError(
                "Attempted to fetch comms characteristic without defining one"
            )
        return self.marked_characteristic

    @property
    def bus(self) -> MessageBus:
        """Property which returns the bus of this application if it is defined"""
        if self._bus is None:
            raise RuntimeError(
                "Message bus of the application was set to None, application cannot operate"
                "without the bus"
            )
        return self._bus
