# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT


from .MUX import TCA9548 as MUX
import time
from ..core.error import Error
from ..core.sensor import I2CSensor

# import logging
# logging.basicConfig(level=logging.DEBUG)

try:
    import struct
except ImportError:
    import ustruct as struct


class SFM3XXX(I2CSensor):
    __name__ = "SFM3XXX"
    _serial_mode = "I2C"
    _SENSOR_ADDRESS = 0x40
    _units = {
        "volumeflow": "slm",
    }
    _i2c_freq = 4e5

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.reset()
        self.exists = self.sensor_exists()

    def sensor_exists(self):
        """
        test if sensor is plugged on and works proper
        :return: [BOOLEAN] True if test was successful otherwise False
        """
        serial_number = self.get_serial_number()
        attempt = 0
        while attempt < self._max_attempts:
            if isinstance(serial_number, int) and serial_number != 0:
                self._logger.info("Serial number: %s", serial_number)
                self.prepare_measurement()
                return True
            else:
                self._logger.warning("Reading serial number failed. Resetting...")
                rst = self.reset()
                self._logger.debug("Reset status: %s", rst)
                attempt += 1
                serial_number = self.get_serial_number()

        self.error = Error().crc(self)
        return False

    def reset(self):
        """
        reseting the sensor
        :return: True for successful reset else False
        """
        try:
            self.txrx([0x20, 0x00], readlen=0)
            time.sleep(0.1)
            return True
        except IOError:
            return False

    def get_serial_number(self):
        """
        reads unique serial number of sensor
        :return: [STRING] serial number of the sensor
        """
        serial_number = 0
        self.error = None
        data = self.txrx([0x31, 0xAE], readlen=6)
        if data is not None:
            check = [
                Error.checksum([data[0], data[1]], data[2], crc_init=0x00)[1],
                Error.checksum([data[3], data[4]], data[5], crc_init=0x00)[1],
            ]
            if False not in check:
                serial_number = data[0]
                for i in [1, 3, 4]:
                    serial_number <<= 8
                    serial_number += data[i]
                self.serial_number = serial_number
            else:
                self._logger.warning("CRC failed while serial number is read")
                self.error = Error().crc(self)
        else:
            self.error = Error().read(self)

        self._logger.debug("Got serial number: %s", serial_number)
        return serial_number

    def prepare_measurement(self):
        """
        initialises a continuous measurement of the mass flow
        :return: [BOOLEAN]: continuous measurement established (True = successful | False = failed)
        """
        data = self.txrx([0x10, 0x00], readlen=3)
        attempts = 0
        while data is None:
            attempts += 1
            data = self.txrx([0x10, 0x00], readlen=3)
            self._logger.warning(
                "Failed to prepare measurement (%s/%s).", attempts, self._max_attempts
            )
            if attempts > self._max_attempts:
                self.mux.close_all_ports()
                self.error = Error().read(self)
                break

        if data is not None and 0xFF not in data[:2]:
            self._logger.info("Started measurement cycle.")
            return True
        else:
            self.mux.close_all_ports()
            self.error = Error().read(self)
            self._logger.warning("Failed to initialize measurement cycle.")

        return self.error

    def get_data(self, scale_factor: int = 140, offset: int = 32000):
        """
        :param scale_factor: sensor specific parameter for the calculation of the volumeflow
        :param offset: sensor specific parameter for the calculation of the volumeflow
        :return: data dictionary
        :rtype: dict
        """
        res = self.txrx([], readlen=3)
        self._logger.debug("Result bytes: %s", res)
        self.data = self.default_data()

        if res is not None:
            if Error.checksum([res[0], res[1]], res[2], crc_init=0x00)[1]:
                value, crc = struct.unpack(">HB", res)
                flow = round((value - offset) / scale_factor, 3)
                if flow <= -218.807:
                    self.reset()
                    self.prepare_measurement()
                    self.error = Error().read(self)
                    self._logger.warning("Resetting sensor due to overflow.")
                    return self.error
                self.data["values"]["volumeflow"] = {
                    "value": flow,
                    "unit": self._units["volumeflow"],
                }
                self.data["error"] = False
                self._logger.debug("Reading successful: %s", flow)
                return self.data
            else:
                self.mux.close_all_ports()
                self.error = Error().crc(self)
                return self.error
        else:
            self.mux.close_all_ports()
            self.error = Error().read(self)
            return self.error
