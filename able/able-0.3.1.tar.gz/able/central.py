#    Copyright (c)  2021  Allthenticate
"""
This module contains the implementation of ABleCentral (A BLE Central) which serves as an abstraction layer
exposing a berkeley-socket like interface for communicating with centrals which connected via the peripheral
server.

References:
Berkeley Sockets: https://en.wikipedia.org/wiki/Berkeley_sockets
"""

# Native modules
import asyncio
import logging
from functools import wraps
from typing import Callable, Dict, List

# Able modules
from able import ABleApplication, ABleCharacteristic

# Configure logging
logger = logging.getLogger(__name__)


def is_connected_wrapper(method: Callable) -> Callable:
    """
    Wrapper for async methods in ABleCentral which checks whether or not the central is still connected before
    calling the function.

    :raises ConnectionError: if no longer connected to the central, disconnect callback already called

    :param method: the method to wrap with the chec
    :return: the wrapped method
    """

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        """Wrapper for the is connected wrapper"""
        if not self.is_connected:
            raise ConnectionError(f"No longer connected to {self}")
        if self.is_closing:
            raise ConnectionError(f"Serverside disconnect already initiated to {self}")
        return await method(self, *args, **kwargs)

    return wrapper


class ABleCentral:
    """
    A platform agnostic BLE central class. This wrapper surrounds methods within the peripheral server
    using a berkeley-socket-like API.

    Class attribute `_app` will be the `ABleApplication` that created this central and is required
    to interact with the central itself.

    :param application: the application that created this central
    :param identifier: the identifier used by the application which uniquely identifies this central
    :ivar str identifier: the identifier of the central, this is the mac address on Ubuntu and a uuid on MacOS
    :ivar asyncio.Event disconnected_event: an event that will only be set when the we get a callback indicating a
        disconnect from the hardware
    :ivar bool is_closing: a boolean indicator if the peripheral has begun to tear down the connection, if this is
        `True` all IO will be blocked
    :ivar int mtu: the maximum transmission unit of the central, if any data is attempted to be sent larger than this
        value an exception will be raised,
    """

    def __init__(
        self,
        application: ABleApplication,
        identifier: str,
        adapter_path=None,
        central_obj=None,
    ):
        """Initializes the Central"""

        # Members for interacting with the app
        self._app = application
        self.identifier = identifier

        # State members
        self.disconnected_event: asyncio.Event = asyncio.Event()
        self.is_closing: bool = False  # todo(bernie) implement
        if adapter_path:
            self.adapter_path: str = adapter_path

        # Core Bluetooth object?
        if central_obj:
            self.obj = central_obj

        # Track our data
        self.char_queues: Dict[int, asyncio.Queue[bytes]] = {}

        # Track the char UUIDs which this central is subscribed to
        self.char_subscriptions: List[str] = []

        # WIP
        self.mtu = 256

    @property
    def is_connected(self):
        """Is connected is the same as returning if the disconnected event has not yet been set"""
        return not self.disconnected_event.is_set()

    def __del__(self):
        """TODO(Bernie) is there cleanup we need to do here?"""

    def __str__(self):
        return f"ABleCentral {self.identifier}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other) -> bool:
        return self.identifier == other.identifier

    @is_connected_wrapper
    async def is_alive(
        self,
        message: bytes = b"ping",
        response_expected: bool = False,
        expected_value: bytes = None,
    ) -> bool:
        """
        The is alive method will send a ping message to the central and await a response if that is expected. If a
        response is expected, the response will be verified against the expected value

        TODO(Bernie): specify a timeout

        :param message: what message should be used as the is alive check (default value=b'ping')
        :param response_expected: `True` if the central will send a response to be checked, `False` otherwise
        :param expected_value: the expected bytes to receive if a response is expected
        :return: `True`, if the central was able to receive the ping (if applicable sent correct response), `False`
            otherwise
        """
        raise NotImplementedError()

    async def close(self) -> None:
        """
        Calls the disconnect command in the ABleApplication that owns this central. This will also set the is closing
        member to true to indicate that the process of tearing down the connection has begun and no more operations
        should happen.

        :return: None
        """
        if not self.is_connected:
            logger.info(f"No longer connected to {self}, close is a NOOP")
            return

        await self._app.disconnect(self)

    @property
    def dbus_path(self) -> str:
        """
        Property which returns a bluezdbus path using the identifier of the device, not that this should only be used
        on the linux backend.

        # TODO(Bernie): Don't allow use if not on linux, or move to somewhere else

        :return: a dbus object path for this device
        """
        return f"{self.adapter_path}/dev_" + self.identifier.replace(":", "_")

    @is_connected_wrapper
    async def send(
        self, data: bytes, characteristic: ABleCharacteristic = None
    ) -> None:
        """
        Berkeley socket style send function. Takes in data and by default notifies the central through the comms
        characteristic but an alternate characteristic can be provided.

        :raises ValueError: if the data is longer than the MTU of the device

        :param data: the data to send to the characteristic
        :param characteristic: an alternate characteristic to send the data on via notifying the device
        :return: None
        """

        # If the size of payload is greater than the MTU of the central, raise a ValueError
        if len(data) > self.mtu:
            raise ValueError(
                "Size of payload is larger than the MTU of the central device."
            )

        # Get the comms characteristic by default unless an alternate is passed in
        if characteristic is None:
            characteristic = self._app.communication_characteristic

        # Send using the target characteristic
        await characteristic.notify_central_of_change(self, data=data)

    @is_connected_wrapper
    async def recv(
        self, characteristic: ABleCharacteristic = None, timeout: int = None
    ) -> bytes:
        """
        Berkeley socket recv function, waits until there is data on the recv queue and returns data once it is
        populated, an optional timeout can be passed in.

        :raises TimeoutError: if the queue is empty after the timout passed in

        :param timeout: an optional timeout, defaults to None
        :param characteristic: the characteristic that you want to receive data from
        :return: returns data from this centrals data queue which stores writes the central did to the communications
            characteristic
        """

        if characteristic is None:
            characteristic = self._app.communication_characteristic

        # Do some magic so if this central disconnects this will terminate
        async def timeout_on_disconnect():
            await self.disconnected_event.wait()
            raise ConnectionError("No longer connected!")

        # This guy will wait to see if data gets put on the characteristic queue from the central
        async def _recv():
            return await asyncio.wait_for(
                self.char_queues[hash(characteristic)].get(), timeout=timeout
            )

        try:
            done, pending = await asyncio.wait(
                [timeout_on_disconnect(), _recv()], return_when=asyncio.FIRST_COMPLETED
            )

            # After doing the wait we need to gather the timout on disconnect coro and cancel it
            gather = asyncio.gather(*pending)
            gather.cancel()
            try:
                await gather
            except asyncio.CancelledError:
                pass

            # Return the result from the wait
            return done.pop().result()
        except ConnectionError as e:
            raise IOError("Unable to recv from central that disconnected") from e

    def flush_buffers(self) -> None:
        """
        Clears all of the recv queues for the central, this is useful if a previous communication timed out and you
        require a fresh buffer before starting a new interaction.

        :returns: None
        """
        for char, queue in self.char_queues.items():
            while not queue.empty():
                queue.get_nowait()
            logger.debug(f"Cleared the queue for {self} for characteristic hash {char}")
