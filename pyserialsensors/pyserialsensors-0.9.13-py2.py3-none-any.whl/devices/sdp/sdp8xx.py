# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Sensor Class for SDP8XX

"""

# import logging
# logging.basicConfig(level=logging.DEBUG)
from ...core.error import Error
from ...core.sensor import I2CSensor


# https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Differential_Pressure/Sensirion_Differential_Pressure_Sensors_SDP8xx_Digital_Datasheet.pdf
class SDP8XX(I2CSensor):
    """
    Differential Pressure sensor SDP8XX 125Pa and 8500
    """

    __name__ = "SDP8XX"
    _units = {"diff_pressure": "Pa", "temperature": "C"}

    _i2c_freq = 10e3
    _SENSOR_ADDRESS = 0x25
    _crc_check_init = 0xFF
    _temperature_scale_factor = 200  # 1/°C
    _temperature_unit = "deg C"

    _cmd_cont_meas_diff_pressure_avg = [0x36, 0x03]
    _cmd_cont_meas_diff_pressure = [0x36, 0x08]
    _cmd_cont_meas_diff_mass_avg = [0x36, 0x15]
    _cmd_cont_meas_diff_mass = [0x36, 0x1E]
    _cmd_stop_cont_meas = [0x3F, 0xF9]
    _cmd_single_meas_mass = [0x36, 0x24]
    _cmd_single_meas_pressure = [0x36, 0x2F]
    _cmd_soft_rst = [0x00, 0x06]
    _cmd_product_identifier = [0x36, 0x7C, 0xE1, 0x02]

    __supported_sensors = {
        "030201": {"id": "SDP800-500Pa", "max_pressure": 500},  # noqa: E501
        "03020A": {"id": "SDP810-500Pa", "max_pressure": 500},  # noqa: E501
        "030204": {"id": "SDP801-500Pa", "max_pressure": 500},  # noqa: E501
        "03020D": {"id": "SDP811-500Pa", "max_pressure": 500},  # noqa: E501
        "030202": {"id": "SDP800-125Pa", "max_pressure": 125},  # noqa: E501
        "03020B": {"id": "SDP810-125Pa", "max_pressure": 125},
    }  # noqa: E501

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.product_number = None
        self.exists = self.sensor_exists()

    def sensor_exists(self):
        """Test if sensor is plugged in and works proper
        :return: [BOOLEAN] True if test was successful otherwise False
        """
        self.reset()
        sn = self.get_serial_number()
        self._logger.debug("Got serial sn: %s", sn)

        if isinstance(sn, int) and sn != 0:
            return True
        else:
            self.error = Error().crc(self)
            return False

    def reset(self):
        """Reseting the sensor
        :return: True for successful reset else False
        """
        try:
            self.txrx(self._cmd_soft_rst, readlen=0)
            self.txrx(self._cmd_stop_cont_meas, readlen=0)
            return True
        except IOError:
            return False

    def crc_check(self, ba: bytearray):
        """
        :param ba: byte array with n*3 entries. Two data bytes are followed by one crc check.
        :return: list of booleans with len n indicating crc results
        """
        crc = [False] * int(len(ba) / 3)
        for i in range(0, len(ba), 3):
            crc[int(i / 3)] = Error().checksum(
                byte_values=[ba[i], ba[i + 1]], crc_value=ba[i + 2], crc_init=0xFF
            )[1]
        return crc

    def check_if_supported(self, ba):
        if ba not in self.__supported_sensors.keys():
            return False
        return True

    def get_raw_serial(self):
        self.txrx(self._cmd_product_identifier[:2], readlen=0)
        self.txrx(self._cmd_product_identifier[2:], readlen=0)
        ba = self.mux.receive(self._SENSOR_ADDRESS, self.mux_port, readlength=18)
        return ba

    def get_serial_number(self):
        """Reads unique serial number of sensor
        :return: [STRING] serial number of the sensor
        """
        self.serial_number = None
        self.error = None
        ba = self.get_raw_serial()

        if ba is not None and len(ba) == 18:

            crc = self.crc_check(ba)

            # Product number
            if crc[0] and crc[1]:
                hex_str = ""
                for i in [0, 1, 3, 4]:
                    hex_str += f"{ba[i]:02X}"

                if not self.check_if_supported(hex_str[:-2]):
                    self.error = Error().unsupported_sensor(self)
                    return self.error

                self.product_number = hex_str[:-2]
                self.sensor_type = self.__name__
            else:
                self.error = Error().crc(self)
                return self.error

            # Serial number
            if crc[2] and crc[3] and crc[4] and crc[5]:
                binary_str = ""
                for i in [6, 7, 9, 10, 12, 13, 15, 16]:
                    bybi = str(bin(ba[i])[2:])
                    binary_str += bybi.zfill(8)
                self.serial_number = int(binary_str, 2)
                return self.serial_number
            else:
                self.error = Error().crc(self)
                return self.error
        else:
            self.error = Error().read(self)
            return self.error

    def prepare_measurement(self):
        self.start_continuous_measurement()
        ba = self.get_raw_data()
        if ba is not None and len(ba) == 9:
            self.crc_check(ba)
            self.scale_factor = ba[6] << 8 | ba[7]
            return True
        else:
            self.mux.close_all_ports()
            self.reset()
            self.error = Error().read(self)
            return self.error

    def start_continuous_measurement(self):
        self.txrx(self._cmd_cont_meas_diff_pressure, readlen=0)

    def get_raw_data(self):
        return self.txrx([], readlen=9)

    def get_data(self):
        """
        :return: data dictionary
        :rtype: dict
        """
        data = self.default_data()
        ba = self.get_raw_data()

        if ba is not None and len(ba) == 9:
            # Perform crc check.
            crc = self.crc_check(ba)
            if crc[0] and crc[1] and crc[2]:

                k_dp = self.bytes_to_u16(ba[6], ba[7])  # 1 / Pa
                if k_dp == 0:
                    self._logger.warning("Differential pressure scale == 0")
                    return Error().read(self)

                # Calculate physical quantities
                dp = self.getS16(ba[0], ba[1]) / k_dp  # Pa
                T = self.getS16(ba[3], ba[4]) / self._temperature_scale_factor  # °C

                # Setup return values
                data["values"] = {}
                data["values"]["temperature"] = {
                    "value": round(T, 2),
                    "unit": self._units["temperature"],
                }
                data["values"]["diff_pressure"] = {
                    "value": round(dp, 3),
                    "unit": self._units["diff_pressure"],
                }

                # Mark values as valid
                data["error"] = False

            else:
                self._logger.debug("CRC Error [%s, %s, %s]", crc)
                self.error = Error().crc(self)
                data = self.error
                self.reset()
                self.prepare_measurement()
        else:
            data = Error().read(self)
            self.reset()
            self.prepare_measurement()

        return data
