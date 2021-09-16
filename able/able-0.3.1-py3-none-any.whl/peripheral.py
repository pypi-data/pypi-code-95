#    Copyright (c)  2021  Allthenticate
"""
This module contains the implementation of ABlePeripheralServer (A BLE Peripheral Server) which serves as a wrapper
around the platform specific implementations of BLE applications with services, characteristics and advertisements
within this library and acts as an abstraction layer following the Berkeley Socket API for handling BLE comms.
"""
import asyncio
import logging

# Native modules
import sys
from typing import Callable, List, Optional, Union

# Able modules
from able import ABleApplication
from able.advertisement import ABleAdvertisement
from able.central import ABleCentral
from able.characteristic import ABleCharacteristic
from able.service import ABleService

# Setup logging
logger = logging.getLogger(name=__name__)


class ABlePeripheralServer:
    """
    A platform agnostic Ble Peripheral Server Class. This class serves as the high level client for
    the ABle library and serves as the main interface into the low level platform specific-backends.

    Class attribute `_app` will be the `AbleApplication` for the platform this server is running on (eg. BluezDbus App).

    Note that this class doesn't track the advertisements, services, nor characteristics that the application
    tracks under the hood.

    :param name: The name you wish to bind to this application on the DBus, defaults to "ABle"
    :param auto_recover: Set to `True` if you want the underlying application to attempt to recover on driver or
        other incidents
    """

    def __init__(
        self,
        name: str = "ABle",
        auto_recover: bool = True,
        adapter_path: Optional[str] = None,
        loop=asyncio.get_event_loop(),
    ):
        """Constructor method for the ABlePeripheralServer"""
        self.name = name

        # Create an application for your platform with the name provided
        self._app = ABleApplication(
            name=self.name, adapter_path=adapter_path, auto_recover=auto_recover
        )

        # Track an event loop
        self.loop = loop

    async def setup_peripheral_server(self) -> None:
        """
        Handle all the setup that the underlying application needs to do within the running event loop. This needs to
        be a separate asynchronous function from the initializer for the class because the `setup()` function for the
        app may be async as well.

        TODO(Bernie): Is there a scenario where we have the `__init__()` call this directly?

        :return: None
        """
        # Do any setup the underlying application needs to do
        await self._app.setup()

    async def add_advertisement(self, advertisement: ABleAdvertisement) -> None:
        """
        Add an advertisement to the peripheral server. Note that the underlying application manages
        checking whether or not you are over the advertisement limit, if the advertisement has already
        been added and more on a platform specific basis.

        TODO(Ori): As we develop the OSX backend there may be duplicated code in the `_app.add_advertisement()`
            implementation that we should extract to here?

        :param advertisement: An instance of `ABleAdvertisement` to add to the application this server is running.
        :return: None
        """
        # Add the advertisement to the app
        logger.debug(f"Adding advertisement {advertisement} to the peripheral server.")
        await self._app.add_advertisement(advertisement=advertisement)

    async def remove_advertisement(self, advertisement: ABleAdvertisement) -> None:
        """
        Removes an advertisement from the underlying application, note that the application will handle
        removal with a bunch of validation.

        TODO(Bernie): Ensure that this works at runtime, we should be able to have the APS remove an advert
            and refresh the application to make it vanish.

        :param advertisement: The advertisement you want to have removed from the server.
        :return: None
        """
        logger.debug(
            f"Removing advertisement {advertisement} from the peripheral server."
        )
        await self._app.remove_advertisement(advertisement=advertisement)

    def add_service(self, service: ABleService) -> None:
        """
        Adds a BLEService to the peripheral server using the underlying application.

        :param service: the service to add to the application
        :return: None
        """
        logger.debug(f"Adding {service} to the peripheral server.")
        self._app.add_service(service)

    def add_characteristic(
        self,
        service: ABleService,
        characteristic: Union[List[ABleCharacteristic], ABleCharacteristic],
        is_comms_char: bool = False,
    ) -> None:
        """
        Adds a BLECharacteristic to the peripheral server using the underlying application.

        :param is_comms_char: `True` will set the characteristic as the communications characteristic,
            defaults to `False`
        :param service: the service to add the characteristic too
        :param characteristic: the characteristic to add, this can also be a list of ABleCharacteristics and each
            will be added for batch adding.
        :return: None
        """
        if isinstance(characteristic, ABleCharacteristic):
            characteristic = [characteristic]

        for chrc in characteristic:
            logger.debug(f"Adding {chrc} to {service}...")

            # If there are no marked characteristics, set this one as the comms
            if self._app.marked_characteristic is None:
                self._app.add_characteristic(
                    service=service, characteristic=chrc, is_comms_char=True
                )
            else:
                self._app.add_characteristic(
                    service=service, characteristic=chrc, is_comms_char=is_comms_char
                )

    def add_connect_callback(self, callback: Callable) -> None:
        """
        Adds a user-defined callback function to the application to be called after connecting to a central device.
        :param callback: the function to be called after a succesfull connection
        :return: None
        """
        if not callable(callback):
            raise TypeError(
                f"The function {callback} that is trying to be added as a connection callback is not callable"
            )

        logger.debug(
            f"Adding user-defined callback {callback} to be called after connection"
        )
        self._app.add_connect_callback(callback)

    def add_disconnect_callback(self, callback: Callable) -> None:
        """
        Adds a user-defined callback function to the application to be called after disconnecting from a central device.
        :param callback: the function to be called after a succesfull disconnect
        :return: None
        """
        if not callable(callback):
            raise TypeError(
                f"The function {callback} that is trying to be added as a disconnect callback is not callable"
            )

        logger.debug(
            f"Adding user-defined callback {callback} to be called after disconnect"
        )
        self._app.add_disconnect_callback(callback)

    async def listen(self, remove_connected: bool = False) -> None:
        """
        Listen is the equivalent its Berkeley Socket API counterpart, it will handle any binding that is required
        and sets the application to be in a "listening state".

        :param remove_connected: if `True` remove all currently connected centrals, (default is `False`)
        :return: None
        """
        if remove_connected:
            raise NotImplementedError("This feature is not yet implemented")

        await self._app.start_interface()

    async def accept(self) -> ABleCentral:
        """
        Blocking call which polls the new connection queue (NCQ) of the underlying application to see if there are any
        new connections. Will only return a ABleCentral once it is present on the NCQ and the app's connected central
        dict.

        :return: A newly connected ABleCentral object ready to be interacted with
        """

        # Wait until the app signals it has a new connection via an event
        await self._app.has_new_central.wait()

        # Pop the new central off of the 'queue'
        new_central = self._app.new_connection_queue.pop()
        logger.debug(new_central)

        # If there are no more centrals in the queue, clear the event
        if len(self._app.new_connection_queue) == 0:
            self._app.has_new_central.clear()

        # Return the new central
        return new_central

    async def broadcast(
        self, data: Union[bytes, str], characteristic: ABleCharacteristic = None
    ) -> None:
        """
        This function will notify all connected centrals on the provided characteristic of new data, for example
        notifying all centrals of the battery level, a state of this peripheral, etc.

        # TODO(Bernie): How should we handle this with possibly different MTU's for different centrals

        :param characteristic: the characteristic to notify all connected centrals on,
            defaults to the comms characteristic
        :param data: the data to notify the centrals on
        :return: None
        """

        # If the characteristic is none, default to the communication characteristic
        if characteristic is None:
            characteristic = self._app.communication_characteristic

        # If is a string is passed in, encode it
        if isinstance(data, str):
            data = data.encode("utf-8")

        logger.info(f"Broadcasting {data!r} on {characteristic}.")

        await characteristic.broadcast(data)

    async def close(self) -> None:
        """
        Equivalent to the socket API's close, this will cleanup all existing connections that the app is managing
        and trigger all cleanup within the app (eg. removing match rules).

        :return: None
        """
        if sys.platform == "darwin":
            self._app.stop()
        elif sys.platform == "linux":
            for connected_central in list(self._app.connected_centrals.values()):
                await connected_central.close()
