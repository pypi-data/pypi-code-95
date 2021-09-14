# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
    Module for I2C Multplexers

    Supported MUX:
      + TCA9548A
      + PCA9548A
"""

import time
from pyftdi.i2c import I2cNackError, I2cIOError
import logging


class TCA9548:
    # Supported adress space
    MUX_ADDRESS_LIST = range(0x70, 0x77 + 1)
    # Port adresses
    MUX_PORT_LIST = range(8)
    # Device delay
    __DELAY = 0.001
    # Maximum number of communication attempts
    __MAX_ATTEMPTS = 10

    def __init__(self, bus, addr, loglvl=logging.INFO, **kwargs):
        self.bus = bus
        self.address = addr
        self._state = None
        if self.address and bus:
            self._logger = logging.getLogger(str(self))
            self._logger.setLevel(loglvl)

    def __str__(self):
        if self.address:
            return f"MUX{self.address:02x}@{self.bus.ftdi._usb_dev.serial_number}"
        return f"No address assigned"

    def connected(self):
        # Check if something is listening on the given address
        for i in range(3):
            self._logger.debug(f"Polling")
            try:
                if self.bus.poll(self.address):
                    # Test the connected device by trying to close all
                    state = self.get_state()
                    self.close_all_ports()
                    # Check state
                    state = self.get_state()
                    if state == 0:
                        self._logger.debug(f"Connected")
                        return True
            except (I2cNackError, I2cIOError):
                pass
        return False

    def get_state(self):
        msg = None
        try:
            msg = self.bus.read(self.address)[0]
        except (I2cIOError, I2cNackError):
            pass
        return msg

    def open_port(self, Port):
        # Check if only on port is requested to be opened
        if type(Port) is int:
            Port = [Port]
        elif type(Port) is not list:
            raise TypeError("Port type is {type(Port)} only int and list supported")

        # Get current port states
        cmd = self.get_state()

        # Modify state if additional ports
        # were requested to be opened
        for port in Port:
            cmd = cmd | (1 << port)

        # Apply changes
        self.write(cmd)
        return cmd

    def open_single_port(self, port: int):
        """
        Open a single port
        """
        cmd = 1 << port
        self._state = self.get_state()

        if cmd != self._state:
            self.write(cmd)
            state = self.get_state()
            if state == 2 ** port:
                self._logger.debug("Successfully opened port %s only.", port)
            else:
                self._logger.warning("Failed to open %s.", port)

            self._state = state
        return self._state

    def write(self, cmd):
        attempt = 0
        while attempt < self.__MAX_ATTEMPTS:
            try:
                if isinstance(cmd, list):
                    self.bus.write(self.address, cmd)
                else:
                    self.bus.write(self.address, [cmd])

                time.sleep(self.__DELAY)
                return cmd
            except (I2cNackError, I2cIOError):
                attempt += 1
        return False

    def poll(self, addr):
        attempt = 0
        while attempt < self.__MAX_ATTEMPTS:
            try:
                found = self.bus.poll(addr, write=True)
                if found:
                    self._logger.info(f"Found device @{addr:02x}h")
                return found
            except (I2cNackError, I2cIOError):
                attempt += 1
        return False

    def is_open(self, port):
        state = self.get_state()
        if (state & (1 << port)) >> port == 0:
            return False
        return True

    def send(self, port, addr, cmd):
        """
        sending command to the sensor
        :param device: [OBJECT] I2C device
        :param cmd: [BYTEARRAY] command
        :param kwargs: {port: [INTEGER] multiplexer port, close: [BOOLEAN] True = close ports after writing}
        :return: [BOOLEAN] True if sending was successful
        """
        self.open_single_port(port)
        try:
            self.byte_logger(cmd, port, addr)
            self.bus.write(addr, cmd)
            time.sleep(self.__DELAY)
            return True
        except (I2cNackError, I2cIOError):
            self.close_all_ports()
            return False

    def byte_logger(self, cmd, port, addr, sep="->"):
        log_str = "["
        if cmd is not None and len(cmd) > 0:
            log_str += f"{cmd[0]:02x}"
            if len(cmd) > 1:
                for c in cmd[1:]:
                    log_str += f" {c:02x}"
        log_str += f"] {sep} {addr:02x}@{port}"
        self._logger.debug(log_str)

    def exchange(self, addr: int, port: int, cmd, readlength=1):
        """
        exchanging data with the sensor
        :param cmd: [BYTEARRAY] command
        :param device: [OBJECT] I2C device
        :param kwargs: {port: [INTEGER] multiplexer port,
                        close: [BOOLEAN] True = close ports after writing,
                        readlength: [INTEGER] expected length of the received data}
        :return: [BYTEARRAY] data if exchange is successful else None
        """
        if isinstance(cmd, int):
            cmd = [cmd]
        elif not isinstance(cmd, list):
            raise AttributeError(f"Expected int or list not {type(cmd)}")

        self.open_single_port(port)
        state = self.send(port, addr, cmd)

        self._logger.debug(f"{cmd} -> {addr:02x}h")
        if not state:
            data = None
            self._logger.error("Failed to write %s to %s@%s", cmd, port, addr)
        else:
            data = self.receive(addr, port, readlength=readlength)
        return data

    def receive(self, addr, port, readlength=1):
        """
        reading data from sensor
        :param device: [OBJECT] I2C device
        :param readlength: [INTEGER] length of the expected data
        :param kwargs: {port: [INTEGER] multiplexer port,
                        close: [BOOLEAN] True = close ports after writing,
                        readlength: [INTEGER] expected length of the received data}
        :return: [BYTEARRAY] data if reading was successful else None
        """
        self.open_single_port(port)

        try:
            ba = self.bus.read(addr, readlen=readlength)
            self.byte_logger(ba, port, addr, sep="<-")
            time.sleep(self.__DELAY)
            self._logger.debug(f"{addr:02x}h -> {ba}")
            return ba
        except (I2cNackError, I2cIOError):
            self._logger.error("Failed to read from %s@%s", port, addr)
            self.close_all_ports()
            return None

    def close_all_ports(self):
        """
        closing all ports on the multiplexer. It is necessary of more than one multiplexer is in use
        :return: [BOOLEAN] True if ports are closed successfully else False
        """
        self.bus.write(self.address, [0x00])
        self.state = 0
        time.sleep(self.__DELAY)
