# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Sensor classes for different serial communication interfaces
"""


import struct
import logging
import time

from pyftdi.i2c import I2cNackError, I2cIOError
from pyftdi.ftdi import FtdiError
from pyftdi.usbtools import UsbTools, UsbToolsError
from .i2controller import MUX
from serial.tools import list_ports
from ..core.i2controller import MmsSpiController as SpiController
from ..core.i2controller import MmsI2cController as I2cController


logging.getLogger("pyftdi").setLevel(logging.ERROR)


class Sensor:
    """
    Abstract sensor class
    """

    __name__ = None
    _units = {}
    _max_attempts = 5
    _delay = 2e-2
    serial_number = None
    sensor_id = None
    ftdi_serial = None
    description = "tba"

    # Holds last result
    data = {}
    error = None

    # If an error occured while communicating
    # with the associated FTDI this flag is set to true
    # such that all other sensors connected to the same
    # FTDI are re-initilized. This ensures that all
    # calibration data and measurement settings are in place
    # after a power shortage.
    disconnected_ftdi = False

    def default_data(self):
        """
        Standard result output
        """
        return {
            "object": "DATA",
            "sensor_type": self.__name__,
            "error": True,
            "SENSORserial": self.serial_number,
            "id": self.sensor_id,
            "FTDIserial": self.ftdi_serial,
            "values": {},
        }

    @staticmethod
    def byte_to_float(arr: bytearray):
        """
        Convert a 32-bit bytearray to IEEE754 float
        :returns: Conversion result
        :rtype: float
        """
        if len(arr) == 4:
            struct_float = struct.pack(">BBBB", arr[0], arr[1], arr[2], arr[3])
            float_value = struct.unpack(">f", struct_float)[0]
        else:
            raise ValueError(f"Incorrect length of arr. Expected 4 got {len(arr)}")
        return float_value

    @classmethod
    def int32(cls, val):
        """
        Translates a 24b-unsigned-interger to a 32b-signed-integer
        :param x: 24b-unsigned integer
        :returns: 32b-bit conversion result
        """
        if val > 0xFFFFFFFF:
            raise OverflowError
        if val > 0x7FFFFFFF:
            val = int(0x100000000 - val)
            if val < 2147483648:
                val = -val
            else:
                val = -2147483648
        return val

    @classmethod
    def bytes_to_u16(cls, msb: int, lsb: int):
        """
        Converts two bytes to unsigned 16bit ingeter
        :param msb: most significant bit
        :param lsb: least significant bit
        """
        return (msb << 8) | lsb

    @classmethod
    def get_float(cls, arr):
        """
        Compile IEEE754 Float from bytes
        :param data: bytearray of length 4
        :returns: converted float
        :rtype: float
        """
        float_value = None
        if len(arr) == 4:
            # read 4 element hex array to float following IEEE754
            struct_float = struct.pack(">BBBB", arr[0], arr[1], arr[2], arr[3])
            float_value = struct.unpack(">f", struct_float)[0]
        return float_value

    def prepare_measurement(self):
        """
        Commands that have to be run prior to a measurement
        """
        pass

    def get_data(self):
        pass

    def set_data(self):
        pass

    def register(self):
        info = {}
        info["identifier"] = self.__name__
        info["serialnumber"] = self.serial_number
        info["description"] = self.description
        info["port"] = self.ftdi_serial
        info["channel"] = []
        return info

    @property
    def serialnumber(self):
        """compatibility"""
        return self.serial_number


class SPISensor(Sensor):
    """
    Standardized SPI sensor class
    """

    # On UM232H CS0 => D3
    _serial_mode = "SPI"
    device = None

    def __init__(
        self,
        bus: "SpiController",
        cs: int,
        sensor_id: str = None,
        loglvl: int = logging.WARNING,
    ):
        self.cs = int(cs)
        self.bus = bus
        self.sensor_type = self.__name__
        self.sensor_id = sensor_id
        self.ftdi_serial = bus.ftdi.usb_dev.serial_number
        self._logger = logging.getLogger(self.__str__())
        self._logger.setLevel(loglvl)

    def default_data(self):
        data = super().default_data()
        data["CS"] = self.cs
        return data

    def txrx(self, reg: int, val=None, readlen: int = 1):
        """
        Sending and receiving data to and from the sensor
        :param reg: register to write to
        :param val: value to be sent
        :param readlen: Number of values to be read from sensor
        :returns: received data
        :rtype: bytearray
        """
        i = 0

        # Cache bus information in case of connection loss
        url = self.bus.url
        mux = self.bus.CS_MUX
        frequency = self.bus.frequency

        while i < self._max_attempts:
            try:
                if val is not None:
                    data = self.device.exchange([reg, val], readlen=readlen)
                else:
                    data = self.device.exchange([reg], readlen=readlen)
                if len(data) == 0:
                    data = None
                return data

            except (I2cNackError, I2cIOError):
                self._logger.error(
                    "Communication failure. (%s/%s)", i, self._max_attempts
                )
                i += 1
                data = None

            except FtdiError:
                """
                This error indicates that the communcation with the FTDI was
                broken this can be caused due to connection problems or power
                losses. First the interface to the FTDI has to be reset.
                Afterwards all connected sensors have to be reinitialized.
                disconnected_ftdi == True indicates the parent class that all
                sensors should be reinitialized.
                """
                attempt = 0
                self.disconnected_ftdi = True
                sleeping_time = 5
                while attempt < self._max_attempts:
                    try:
                        UsbTools.flush_cache()
                        self.bus = SpiController(CS_MUX=mux)
                        self.bus.ftdi.open_from_url(url)
                        self.bus.configure(url, frequency=frequency)
                        self._logger.info(
                            "Opened new connection. (f=%d kHz)",
                            int(self.bus._frequency / 1000.0),
                        )
                        break
                    except (FtdiError, UsbToolsError, ValueError):
                        attempt += 1
                        self._logger.error(
                            "FTDI connection issue \
                                            - Attempt (%s/%s)",
                            attempt,
                            self._max_attempts,
                        )
                    if attempt == self._max_attempts:
                        # if reconnection attempts failed the device
                        # is put to rest and will be asked again
                        attempt -= 1
                        self._logger.error(
                            "Failed to reconnect. Wait %s seconds\
                                before trying againg once.",
                            sleeping_time,
                        )
                        time.sleep(sleeping_time)
                return None

    def read_u8(self, reg: int):
        """
        Reading 8bit integer from the sensor
        :param reg: register to be read
        """
        out = self.txrx(reg)
        if out is not None:
            out = out[0]
        return out

    def read_u16(self, reg: int):
        """
        Reading 8bit integer from the sensor
        :param reg: register to be read
        """
        out = self.txrx(reg, readlen=2)
        if out is not None:
            out = int((out[0] << 8) + out[1])
        return out

    def write_u8(self, reg: int, val: int):
        """
        Writing 8bit integer from the sensor
        :param reg: register to write to
        :param val: value to be sent
        """
        self.txrx(reg, val=val, readlen=0)


class I2CSensor(Sensor):
    """
    Generalized I2C sensor
    """

    _clk_stretch = True
    _serial_mode = "I2C"
    mux_port = 0
    mux = MUX(None, None)
    _SENSOR_ADDRESS = -1

    def __init__(
        self,
        bus: "I2cController",
        mux: "MUX",
        mux_port: int,
        loglvl: int = logging.WARNING,
    ):
        """
        Base class for all I2C Sensors
        :param bus: (core.i2controler.MMS_I2CController) sensor bus object
        :param mux: mux sensor MUX object
        :param mux_port: mux_port sensor MUX port
        :param sensor_id: sensor_id sensor identifier
        """
        self.bus = bus
        self.ftdi_serial = bus.ftdi._usb_dev.serial_number
        self.mux_port = mux_port
        self.mux = mux
        self._logger = logging.getLogger(self.__str__())
        self._logger.setLevel(loglvl)
        self.mux._logger.setLevel(loglvl)

    def default_data(self):
        """
        Default I2C Sensor result data
        """
        data = super().default_data()
        data["MUXaddress"] = self.mux.address
        data["MUXport"] = self.mux_port
        return data

    def __str__(self):
        return f"{self.__name__}@FTDI_{self.ftdi_serial}:\
                MUX/{self.mux.address:02x}/{self.mux_port}"

    def getU16(self, reg1: int, reg2: int):
        """
        Read an unsigned 16-bit value from the specified register, in little
        endian byte order.
        :param reg1: register of the most significant bit (msb)
        :param reg2: register of the most significant bit (lsb)
        """
        # Read registers
        msb = self.txrx(reg1, readlen=1)
        lsb = self.txrx(reg2, readlen=1)

        if None not in [msb, lsb]:
            msb = msb[0]
            lsb = lsb[0]
            self._logger.debug("MSB %s LSB %s", msb, lsb)
            return self.bytes_to_u16(msb, lsb)
        return None

    def getS16(self, reg1: int, reg2: int):
        """
        Read an signed 16-bit value from the specified register, in little
        endian byte order.
        """
        out = self.bytes_to_u16(reg1, reg2)
        if out is not None:
            if out > 32767:
                out -= 65536
        else:
            out = None
        return out

    def getU8(self, cmd):
        """
        Read an unsigned 8-bit value from the specified register, in little
        endian byte order.
        """
        if not isinstance(cmd, list):
            cmd = [cmd]
        elif not isinstance(cmd, list):
            raise TypeError(f"Invalid type {type(cmd)} for cmd.")

        out = self.txrx(cmd, readlen=1)
        if out is not None:
            out = out[0]
        return out

    def getS8(self, cmd):
        """
        Read an signed 8-bit value from the specified register, in little
        endian byte order.
        :param cmd: register to read
        :type cmd: list or int
        """
        if isinstance(cmd, list):
            out = self.getU8(cmd)
        elif isinstance(cmd, int):
            out = self.getU8([cmd])
        else:
            raise TypeError(f"Invalid type {type(cmd)} for cmd.")

        if out is not None and out > 127:
            out -= 256

        return out

    def info(self):
        if self.exists:
            print(
                f"{self.ftdi_serial} | {self.mux.address} | \
                    {self.mux_port} => found {self.__name__}"
            )
            return {
                "SENSORtype": self.__name__,
                "SENSORserial": self.serial_number,
                "FTDIserial": self.ftdi_serial,
                "MUXaddress": self.mux.address,
                "MUXport": self.mux_port,
                "units": self._units,
                "SENSORidentifier": "",
            }
        return False

    def txrx(self, cmd, readlen=3):
        """
        write cmd, read readlen bytes from i2c, perform crc check.
        If successful return data else False
        :param cmd:  [bytearray] i2c command
        :param readlen: [integer] number of bytes to read
        """
        sleeping_time = 5

        if not isinstance(cmd, list):
            self._logger.debug("Sending: %s", cmd)
            cmd = [cmd]

        data = None
        i = 0
        while i < self._max_attempts:
            try:
                if len(cmd) == 0:
                    data = self.mux.receive(
                        self._SENSOR_ADDRESS, self.mux_port, readlength=readlen
                    )
                elif readlen == 0:
                    self.mux.send(self.mux_port, self._SENSOR_ADDRESS, cmd)
                else:
                    data = self.mux.exchange(
                        self._SENSOR_ADDRESS, self.mux_port, cmd, readlength=readlen
                    )
                break
            except (I2cNackError, I2cIOError):
                self._logger.error(
                    "Communication failure. (%s/%s)", i, self._max_attempts
                )
                i += 1
                data = None

            except FtdiError:
                """
                This error indicates that the communcation with the FTDI was
                broken this can be caused due to connection problems or power
                losses. First the interface to the FTDI has to be reset.
                Afterwards all connected sensors have to be reinitialized.
                disconnected_ftdi == True indicates the parent class that all
                sensors should be reinitialized.
                """
                sleeping_time = 5
                attempt = 0
                self.disconnected_ftdi = True
                while attempt < self._max_attempts:
                    try:
                        UsbTools.flush_cache()
                        self.bus.configure(
                            self.bus.url,
                            clockstretching=True,
                            frequency=self.bus._frequency,
                        )
                        self._logger.info(
                            "Opened new connection. (f=%d kHz)",
                            int(self.bus._frequency / 1000.0),
                        )
                        break
                    except (FtdiError, UsbToolsError, ValueError):
                        attempt += 1
                        self._logger.error(
                            "FTDI connection issue \
                                            - Attempt (%s/%s)",
                            attempt,
                            self._max_attempts,
                        )
                    if attempt == self._max_attempts:
                        # if reconnection attempts failed the device
                        # is put to rest and will be asked again
                        attempt -= 1
                        self._logger.error(
                            "Failed to reconnect. Wait %s seconds\
                                before trying againg once.",
                            sleeping_time,
                        )
                        time.sleep(sleeping_time)
                return None

        return data


class UARTSensor(Sensor):
    """
    Generalized UART sensor
    """

    _clk_stretch = True
    _serial_mode = "UART"
    port = None

    def __init__(self, bus):
        """
        Base class for all I2C Sensors
        """
        self.bus = bus
        self._logger = logging.getLogger(self.__str__())

    def default_data(self):
        """
        Default COM Sensor result data
        """
        data = super().default_data()
        data["Port"] = self.port
        return data

    def __str__(self):
        return f"{self.__name__}@{self.port}"

    @staticmethod
    def find_port(ftdi_serial):
        """For a given ftdi_serial number find the correct dev/ path"""
        all_comports = list_ports.comports()
        for cp in all_comports:
            if cp.serial_number == ftdi_serial:
                return cp.device
        return None

    def info(self):
        if self.exists:
            print(f"{self.port} > found {self.__name__}")
            return {
                "SENSORtype": self.__name__,
                "SENSORserial": self.serial_number,
                "Port": self.port,
                "units": self._units,
                "SENSORidentifier": "",
            }
        return False

    def txrx(self, cmd, readlen=3, t_wait=0.1):
        """
        write cmd, read readlen bytes from i2c, perform crc check.
        If successful return data else False
        :param cmd:  [bytearray] i2c command
        :param readlen: [integer] number of bytes to read
        """
        if type(cmd) == list:
            cmd = [cmd]

        self.bus.write(cmd)
        data = None
        if readlen > 0:
            resp = self.bus.inWaiting()
            while resp < readlen:
                resp = self.bus.inWaiting()
                time.sleep(t_wait)
            data = self.ser.read(resp)

        return data

    def close_port(self):
        self.ser.close()
