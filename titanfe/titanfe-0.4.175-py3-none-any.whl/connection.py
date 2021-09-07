#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate asyncio connections by wrapping them into a Connection"""

import asyncio
import logging
import pickle

from collections import namedtuple
from typing import Optional

from ujotypes import UjoMap, read_buffer, ujo_to_python, UjoStringUTF8

import titanfe.log
from titanfe.apps.brick_runner.connection import Buffer
from titanfe.ujo_helper import py_to_ujo_bytes
from titanfe.messages import Message

ENCODING = "UJO"
# ENCODING = "PICKLE"

PAYLOAD = UjoStringUTF8("payload")
BUFFER = UjoStringUTF8("buffer")

NetworkAddress = namedtuple("NetworkAddress", ("host", "port"))


def decode_ujo_message(ujo_bytes):
    """Decode ujo bytes into a corresponding python object, but keep an existing "Payload" as Ujo.
    """
    ujoobj = read_buffer(ujo_bytes)
    _, content = ujoobj[0], ujoobj[1]

    payload = None
    if isinstance(content, UjoMap) and PAYLOAD in content:
        payload = content[PAYLOAD]
        del ujoobj[1][PAYLOAD]
        try:
            buffer = content[BUFFER]
        except KeyError:
            buffer = UjoMap()
        else:
            del ujoobj[1][BUFFER]

    pyobj = ujo_to_python(ujoobj)

    if payload is not None:
        # set payload to the original ujo payload
        pyobj[1]["payload"] = payload
        pyobj[1]["buffer"] = Buffer(buffer)

    return pyobj


class Connection:
    """Wrap an asyncio StreamReader/Writer combination into a connection object.

     Arguments:
         reader (asyncio.StreamReader): the stream reader
         writer (asyncio.StreamWriter): the stream writer
         log (logging.logger): a parent logger
         encoding: "PICKLE" or "UJO"
     """

    def __init__(self, reader, writer, log=None, encoding=ENCODING):
        self.reader = reader
        self.writer = writer
        self.closed = False

        self.log = log.getChild("Connection") if log else titanfe.log.getLogger(__name__)

        if encoding == "PICKLE":
            self.decode = pickle.loads
            self.encode = pickle.dumps
        elif encoding == "UJO":
            self.decode = decode_ujo_message
            self.encode = py_to_ujo_bytes

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @classmethod
    async def open(
        cls, address: NetworkAddress, log: Optional[logging.Logger] = None
    ) -> "Connection":
        """open an asyncio connection to the given address (host, port)"""
        reader, writer = await asyncio.open_connection(*address)
        return cls(reader, writer, log)

    async def close(self):
        """close the connection by closing it's reader and writer"""
        if self.closed:
            return
        self.reader.feed_eof()
        self.writer.close()
        try:
            await self.writer.wait_closed()
        except (ConnectionAbortedError, ConnectionResetError):
            pass
        self.closed = True

    async def receive(self):
        """wait until a message comes through and return it's content after decoding

        Return:
             Message: a message or None if the connection was closed remotely
        """
        message = None
        while not message:
            try:
                msg_len = await self.reader.readexactly(4)
            except (asyncio.IncompleteReadError, ConnectionError):
                self.log.debug("Stream at EOF - close connection.")
                # self.log.debug('', exc_info=True)
                await self.close()
                return

            msg = await self.reader.readexactly(int.from_bytes(msg_len, "big"))

            self.log.debug("received message: %s", msg)
            try:
                msg = self.decode(msg)
            except Exception:
                self.log.error("Failed to decode %r", msg, exc_info=True)
                raise ValueError(f"Failed to decode {msg}")

            try:
                message = Message(*msg)
            except TypeError:
                self.log.error("Received unknown Message format: %s", msg)
                message = None

        self.log.debug("decoded message: %r", message)
        return message

    async def send(self, message):
        """encode and send the content as a message"""
        self.log.debug("sending: %r", message)
        try:
            msg = self.encode(message)
        except Exception:
            self.log.error("Failed to encode %r", message, exc_info=True)
            raise ValueError(f"Failed to encode {message}")

        msg_len = len(msg).to_bytes(4, "big")
        try:
            self.writer.write(msg_len)
            self.writer.write(msg)
            await self.writer.drain()
        except (ConnectionAbortedError, ConnectionResetError):
            await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        message = await self.receive()
        if not message:
            raise StopAsyncIteration

        return message
