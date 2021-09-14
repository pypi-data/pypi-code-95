# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import serial
from serial.tools import list_ports
import struct
import time
import termios
import logging
from ..core.sensor import UARTSensor
from ..core.error import Error
import timeout_decorator

# logging.basicConfig(level=logging.INFO)


class SPS30(UARTSensor):
    """
    UART driver for
    Particulate Matter Sensor for Air Quality Monitoring and Control
    """

    __name__ = "SPS30"
    _serial_mode = "COM"
    __supported_sensors = ["SPS30"]
    _units = {
        "m_03_to_1_0_mu": "1/cm3",
        "m_03_to_2_5_mu": "1/cm3",
        "m_03_to_4_0_mu": "1/cm3",
        "m_03_to_10_0_mu": "1/cm3",
        "n_03_to_0_5_mu": "1/cm3",
        "n_03_to_1_0_mu": "1/cm3",
        "n_03_to_2_5_mu": "1/cm3",
        "n_03_to_4_0_mu": "1/cm3",
        "n_03_to_10_0_mu": "1/cm3",
        "tps": "mum",
    }

    _log = None
    _max_waiting_time = 0.5  # [s]
    __START_STOP_BYTE = 0x7E

    # Commands
    __START_MEASUREMENT = [0x00, 0x00, 0x02]  # Start a measurement
    __START_DATA_TYPE_754 = [0x01, 0x03, 0xF9]  # Big endian IEEE 754
    __START_DATA_TYPE_INT = [0x01, 0x05, 0xF9]  # Big endian 16-Bit integer
    __STOP_MEASUREMENT = [0x00, 0x01, 0x00, 0xFE]  # Stop a measurement
    __READ_DATA = [0x00, 0x03, 0x00, 0xFC]  # Read measurement data
    __SERIAL_NUMBER = [0x03, 0x2B]  # Read serial number
    __PRODUCT_TYPE = [0x00, 0x7E]  # Get product type
    __DEVICE_INFORMATION = [0x00, 0xD0, 0x01]  # Get device information

    def __init__(self, port, scan=False):
        self.port = port
        self.ser = serial.Serial(
            self.port, baudrate=115200, stopbits=1, parity="N", timeout=2
        )
        if not scan:
            self._log = logging.getLogger(name=str(self))
            self.serial_number = self.get_serial_number()
            self.ftdi_serial = self.get_ftdi_serial()

    def __str__(self):
        return f"SPS30@{self.port}"

    def reconnect(self):
        # Find port matching FTDIserial
        port = self.find_port(self.ftdi_serial)
        if port is None:
            return None

        self.port = port
        # Try to initialize port
        try:
            self.ser.close()
            self.ser = serial.Serial(
                self.port, baudrate=115200, stopbits=1, parity="N", timeout=2
            )
        except serial.serialutil.SerialException:
            if self._log is not None:
                self._log.warning("Failed to reconnect.")

    def txrx(self, base_cmd, read=0, sleep=0.02):
        try:
            self.ser.flushInput()
            cmd = [self.__START_STOP_BYTE]
            cmd += base_cmd
            cmd += [self.__START_STOP_BYTE]
            self.ser.write(cmd)
            if self._log is not None:
                self._log.debug(f"Sending: {cmd}")
                self._log.debug(f"Base CMD: {base_cmd}")
            time.sleep(sleep)
            raw = None
            if read != 0:
                toRead = self.ser.inWaiting()
                waiting_time = 0
                while toRead < read:
                    toRead = self.ser.inWaiting()
                    time.sleep(sleep * 5)
                    waiting_time += sleep * 5  # [s]
                    if waiting_time > self._max_waiting_time:
                        if self._log is not None:
                            self._log.warning(f"Timeout: CMD {cmd}")
                        return None

                raw = self.ser.read(toRead)
                if self._log is not None:
                    self._log.debug(f"Received: {raw}")
                # Reverse byte-stuffing
                if b"\x7D\x5E" in raw:
                    raw = raw.replace(b"\x7D\x5E", b"\x7E")
                if b"\x7D\x5D" in raw:
                    raw = raw.replace(b"\x7D\x5D", b"\x7D")
                if b"\x7D\x31" in raw:
                    raw = raw.replace(b"\x7D\x31", b"\x11")
                if b"\x7D\x33" in raw:
                    raw = raw.replace(b"\x7D\x33", b"\x13")
            return raw
        except (termios.error, OSError, serial.serialutil.SerialException):
            return None

    def get_ftdi_serial(self):
        ftdi_serial = "undefined"
        all_comports = list_ports.comports()
        for cp in all_comports:
            if cp.device == self.port:
                ftdi_serial = cp.serial_number
                break
        ftdi_serial = ftdi_serial
        return ftdi_serial

    def sensor_exists(self):
        """
        Check if a sensor is present by reading the serial number
        """
        try:
            serial_number = self.get_serial_number()

        except StopIteration:
            if self._log is not None:
                self._log.info("Stop iteration.")
            self.ser.close()
            return None

        if self._log is not None:
            self._log.info(f"Sensor serial: {serial_number}")

        self.ser.close()
        return serial_number

    def start(self):
        try:
            if self.ser.isOpen():
                self.ser.close()
            self.ser.open()
        except serial.serialutil.SerialException:
            if self._log is not None:
                self._log.error("Failed to start")
            return None
        cmd = self.__START_MEASUREMENT + self.__START_DATA_TYPE_754
        out = self.txrx(cmd)
        if out is None:
            if self._log is not None:
                self._log.error("Error starting device.")

    def prepare_measurement(self):
        return self.start()

    def stop(self):
        out = self.txrx(self.__STOP_MEASUREMENT)
        if out is None:
            if self._log is not None:
                self._log.error("Error starting device.")

    def get_data(self):
        data = self.read_values()
        if data is None:
            if self._log is not None:
                self._log.error("Error fetching values.")

        time.sleep(1.04)  # max sampling intervall according to datasheet
        return data

    def read_values(self):
        raw = self.txrx(self.__READ_DATA, read=47)
        if raw is None:
            self.error = Error().read(self)
            self.reconnect()
            self.prepare_measurement()
            return self.error

        self.data = self.default_data()

        raw = raw[5:-2]

        try:
            m10, m25, m40, m100, n05, n10, n25, n40, n100, s = struct.unpack(
                ">ffffffffff", raw
            )
            self.data["values"] = {}
            self.data["values"]["m_03_to_1_0_mu"] = {
                "value": m10,
                "unit": self._units["m_03_to_1_0_mu"],
            }
            self.data["values"]["m_03_to_2_5_mu"] = {
                "value": m25,
                "unit": self._units["m_03_to_2_5_mu"],
            }
            self.data["values"]["m_03_to_4_0_mu"] = {
                "value": m40,
                "unit": self._units["m_03_to_4_0_mu"],
            }
            self.data["values"]["m_03_to_10_0_mu"] = {
                "value": m100,
                "unit": self._units["m_03_to_10_0_mu"],
            }
            self.data["values"]["n_03_to_0_5_mu"] = {
                "value": n05,
                "unit": self._units["n_03_to_0_5_mu"],
            }
            self.data["values"]["n_03_to_1_0_mu"] = {
                "value": n10,
                "unit": self._units["n_03_to_1_0_mu"],
            }
            self.data["values"]["n_03_to_2_5_mu"] = {
                "value": n25,
                "unit": self._units["n_03_to_2_5_mu"],
            }
            self.data["values"]["n_03_to_4_0_mu"] = {
                "value": n40,
                "unit": self._units["n_03_to_4_0_mu"],
            }
            self.data["values"]["n_03_to_10_0_mu"] = {
                "value": n100,
                "unit": self._units["n_03_to_10_0_mu"],
            }
            self.data["values"]["tps"] = {"value": s, "unit": self._units["tps"]}
            self.data["error"] = False

            return self.data

        except struct.error:
            self.error = Error().read(self)
            self.prepare_measurement()
            return self.error

    @timeout_decorator.timeout(5, timeout_exception=StopIteration)
    def get_serial_number(self):
        cmd = self.__DEVICE_INFORMATION + self.__SERIAL_NUMBER
        raw = self.txrx(cmd, read=24)

        if raw is None:
            return raw
        return raw[5:-3].decode("ascii")

    def close_port(self):
        self.ser.close()
