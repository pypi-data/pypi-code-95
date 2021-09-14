# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Sensor Class for SCD30

Datasheet
https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/CO2/Sensirion_CO2_Sensors_SCD30_Datasheet.pdf

Interface description
https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/9.5_CO2/Sensirion_CO2_Sensors_SCD30_Interface_Description.pdf

"""

import time
from ..core.error import Error
from ..core.sensor import I2CSensor


class SCD30(I2CSensor):
    """
    SCD30 - CO2 and RH/T Sensor Module
    """

    __name__ = "SCD30"
    _serial_mode = "I2C"
    _units = {
        "co2": "ppm",
        "temperature": "C",
        "humidity": "pct",
    }

    _SENSOR_ADDRESS = 0x61
    _crc_check_init = 0xFF
    _clk_stretch = True
    _i2c_freq = 1e3

    # idx 2 + 3: pressure bytes [default 0mBar]
    __cmd_cont_meas = [0x00, 0x10]  # noqa
    __cmd_stop_cont_meas = [0x01, 0x04]  # noqa
    # idx 2 + 3: time bytes [default 2s]
    __cmd_get_measurement_interval = [0x46, 0x00]  # noqa
    # idx 4 + 5: time bytes [default 2s]
    __cmd_set_measurement_interval = [0x46, 0x00, 0x25, 0x00]  # noqa
    __cmd_get_data_rdy = [0x02, 0x02]  # noqa
    __cmd_read_meas = [0x03, 0x00]  # noqa
    __cmd_asc_get_state = [0x53, 0x06]  # noqa
    __cmd_asc_activate = [0x53, 0x06, 0x00, 0x01, 0xB0]  # noqa
    __cmd_asc_deactivate = [0x53, 0x06, 0x00, 0x00, 0x81]  # noqa
    # idx 2 + 3: time bytes [default 2s]
    __cmd_forced_calibration = [0x52, 0x04]  # noqa
    # idx 2 + 3: temperature deg C*100
    __cmd_set_temperature_offset = [0x00, 0x3B]  # noqa
    __cmd_get_temperature_offset = [0x54, 0x03]  # noqa
    # idx 2 + 3: altitude [m]
    __cmd_set_altitude_compensation = [0x00, 0x38]
    __cmd_get_altitude_compensation = [0x51, 0x02]
    __cmd_get_serial_number = [0xD0, 0x33]  # noqa

    __cmd_get_firmware_version = [0xD1, 0x00]  # noqa
    __cmd_soft_rst = [0xD3, 0x04]  # noqa

    __supported_sensors = ["SCD30"]

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        # Identifiers
        super().__init__(*args, **kwargs)
        self.serial_number = None
        self.exists = self.sensor_exists()

    def txrx(self, *args, crc=True, **kwargs):
        """
        Standard txrx module is extended by a crc check
        """
        data = super().txrx(*args, **kwargs)
        if data is not None:
            if crc and False in self.crc_check(data):
                self._logger.warning("CRC check failed.")
                data = None
        return data

    def sensor_exists(self):
        """
        test if sensor is plugged in and works proper
        :returns: True if test was successful otherwise False
        :rtype: bool
        """
        serial_number = self.get_serial_number()

        exists = False

        if isinstance(serial_number, str) and serial_number != "":
            self.serial_number = serial_number
            exists = True
        else:
            self.error = "No connection."
        return exists

    def get_firmware(self):
        data = self.txrx(self.__cmd_get_firmware_version, readlen=3)
        if data is not None:
            return f"{data[0]}.{data[1]}"
        return False

    def get_asc_status(self):
        data = self.txrx(self.__cmd_asc_get_state, readlen=3)

        if data is not None:
            if data[1] == 1:
                return True
            elif data[1] == 0:
                return False
            else:
                return None

    def get_measurement_intervall(self):
        data = None
        for i in range(self._max_attempts):
            data = self.txrx(self.__cmd_get_measurement_interval, readlen=3)
            if data is not None:
                t_int = self.bytes_to_u16(data[0], data[1])
                self._logger.debug(f"Intervall time: %d", t_int)
                return t_int
        return data

    def stop_measurement(self):
        self.txrx(self.__cmd_stop_cont_meas, readlen=0)

    def reset(self):
        """
        reseting the sensor
        :return: True for successful reset else False
        """
        self.txrx(self.__cmd_soft_rst, readlen=0)
        time.sleep(0.5)

    def crc_check(self, ba):
        """
        :param ba: [BYTEARRAY] byte array with crc check sum every third entry
        :return: Array of booleans indicated correct crc check sums
        """
        crc = [False] * int(len(ba) / 3)
        if len(ba) % 3 != 0:
            return crc

        for i in range(0, len(ba), 3):
            crc[int(i / 3)] = Error.checksum(
                byte_values=[ba[i], ba[i + 1]],
                crc_value=ba[i + 2],
                crc_init=self._crc_check_init,
            )[1]
        return crc

    def get_serial_number(self):
        """
        Get device serial number
        :return: [STRING] not supported
        :raises: Warning
        """
        for i in range(self._max_attempts):
            data = self.txrx(self.__cmd_get_serial_number, crc=False, readlen=9)
            if data is not None:
                self.serial_number = ""
                for i in [0, 1, 3, 4, 6, 7]:
                    self.serial_number += chr(data[i])
                return self.serial_number
            else:
                self.error = Error().crc(self)
                msg = "Failed to fetch serial number."
                msg += "(attempt  {i}/{self._max_attempts})"
                self._logger.debug(msg)
        return False

    def set_asc(self, state):
        """
        setup automatic self calibration
        :param amb_pressure: ambiet pressure (default==off)
        ranges from 700-1400mBar
        """
        current_state = self.get_asc_status()
        if current_state != state:
            if state:
                self.txrx(self.__cmd_asc_activate, readlen=0)
            else:
                self.txrx(self.__cmd_asc_deactivate, readlen=0)
        time.sleep(self.measurement_intervall + 1)

    def prepare_measurement(self, amb_pressure=0):
        t0 = time.time()
        self.start_continuous_measurement(amb_pressure=amb_pressure)
        self._logger.debug("Measurement prep. took %d seconds.", int(time.time() - t0))

    def start_continuous_measurement(self, amb_pressure=0):
        """
        initialises a continuous measurement of CO2 temperature and humidity
        :param amb_pressure: ambiet pressure (default==off)
        ranges from 700-1400mBar
        :return: [BOOLEAN]: continuous measurement established
        (True = successful | False = failed)
        """
        intervall = self.get_measurement_intervall()
        if isinstance(intervall, int):
            self.measurement_intervall = intervall
        else:
            self.measurement_intervall = 2

        self.set_asc(True)

        assert amb_pressure == 0 or amb_pressure > 700, "amb_pressure too low"
        assert amb_pressure == 0 or amb_pressure < 1400, "amb_pressure too high"

        amb_pressure = 1000
        if amb_pressure == 0:
            # defaults to 1013.25mBar
            p_lsb = 0x00
            p_msb = 0x00
            p_crc = 0x81

        else:
            p_msb, p_lsb = divmod(amb_pressure, 256)
            p_crc = Error.checksum(
                byte_values=[p_msb, p_lsb],
                crc_value=0x00,
                crc_init=self._crc_check_init,
            )[0]
        cmd = self.__cmd_cont_meas + [p_msb, p_lsb, p_crc]
        # self._logger.warning(f"init cmd not send (legacy) {cmd}")
        self.txrx(cmd)
        time.sleep(self.measurement_intervall + 1)

    def get_data_rdy(self):
        data = self.txrx(self.__cmd_get_data_rdy, readlen=3)
        if data is not None and data[1] == 0x01:
            return True
        self._logger.debug("Data is not ready.")
        return False

    def get_data(self):
        """
        :param scale_factor: [INT] sensor specific parameter for the
        calculation of the volume flow
        :param offset: [INT] sensor specific parameter for the calculation of
        the volume flow
        :return: [DICT] data dictionary
        """

        # Wait until data is ready
        i = 0
        self.data = self.default_data()

        while not self.get_data_rdy():
            i += 1
            time.sleep(2 * self.measurement_intervall / (self._max_attempts - 1))
            if i > self._max_attempts:
                self._logger.warning("Reset.")
                self.error = Error().read(self)
                self.reset()
                self.prepare_measurement()
                return self.error

        ba = self.txrx(self.__cmd_read_meas, readlen=18)
        if ba is not None:
            co2 = int(self.byte_to_float([ba[0], ba[1], ba[3], ba[4]]))
            T = self.byte_to_float([ba[6], ba[7], ba[9], ba[10]])
            RH = self.byte_to_float([ba[12], ba[13], ba[15], ba[16]])
            self.data["error"] = False
            self.data["values"] = {}
            self.data["values"]["co2"] = {"value": co2, "unit": self._units["co2"]}

            self.data["values"]["temperature"] = {
                "value": T,
                "unit": self._units["temperature"],
            }
            self.data["values"]["humidity"] = {
                "value": RH,
                "unit": self._units["humidity"],
            }
            return self.data
        else:
            self.error = Error().read(self)
            self.prepare_measurement()
            return self.error
