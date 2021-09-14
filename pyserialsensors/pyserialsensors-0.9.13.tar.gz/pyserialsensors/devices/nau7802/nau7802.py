# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Sensor Class for NAU7802

"""

import time
from ...core.error import Error
from ...core.sensor import I2CSensor

# import logging
# logging.basicConfig(level=logging.DEBUG)


class NAU7802(I2CSensor):
    """
    Qwiic Scale driver
    """

    __name__ = "NAU7802"

    _SENSOR_ADDRESS = 0x2A

    _units = {
        "adc": "[-]",
    }
    _i2c_freq = 100e3

    # Register
    __REG = {
        "PU_CTRL": 0x00,
        "CTRL1": 0x01,
        "CTRL2": 0x02,
        "OCAL1_B2": 0x03,
        "OCAL1_B1": 0x04,
        "OCAL1_B0": 0x05,
        "GCAL1_B3": 0x06,
        "GCAL1_B2": 0x07,
        "GCAL1_B1": 0x08,
        "GCAL1_B0": 0x09,
        "OCAL2_B2": 0x0A,
        "OCAL2_B1": 0x0B,
        "OCAL2_B0": 0x0C,
        "GCAL2_B3": 0x0D,
        "GCAL2_B2": 0x0E,
        "GCAL2_B1": 0x0F,
        "GCAL2_B0": 0x10,
        "I2C_CONTROL": 0x11,
        "ADCO_B2": 0x12,
        "ADCO_B1": 0x13,
        "ADCO_B0": 0x14,
        "ADC": 0x15,  # Shared ADC and OTP 32: 24
        "OTP_B1": 0x16,  # OTP 23:16 or 7:0?
        "OTP_B0": 0x17,  # OTP 15: 8
        "PGA": 0x1B,
        "PGA_PWR": 0x1C,
        "DEVICE_REV": 0x1F,
    }

    __BIT = {
        # Bits within the PU_CTRL register
        "PU_CTRL": {
            "RR": 0,
            "PUD": 1,
            "PUA": 2,
            "PUR": 3,
            "CS": 4,
            "CR": 5,
            "OSCS": 6,
            "AVDDS": 7,
        },
        # Bits within the CTRL2 register
        "CTRL2": {
            "CHS": 7,
            "CALMOD": 0,
            "CALS": 2,
            "CAL_ERROR": 3,
            "CRS": 4,
        },
    }
    # Bits within the PGA register
    __NAU7802_PGA_CHP_DIS = 0
    __NAU7802_PGA_INV = 3
    __NAU7802_PGA_BYPASS_EN = 4
    __NAU7802_PGA_OUT_EN = 5
    __NAU7802_PGA_LDOMODE = 6
    __NAU7802_PGA_RD_OTP_SEL = 7

    # Bits within the PGA PWR register
    __NAU7802_PGA_PWR_PGA_CURR = 0
    __NAU7802_PGA_PWR_ADC_CURR = 2
    __NAU7802_PGA_PWR_MSTR_BIAS_CURR = 4
    __NAU7802_PGA_PWR_PGA_CAP_EN = 7

    # Allowed Low drop out regulator
    __NAU7802_LDO_Voltage = {
        "2.4": 0b111,
        "2.7": 0b110,
        "3.0": 0b101,
        "3.3": 0b100,
        "3.6": 0b011,
        "3.9": 0b010,
        "4.2": 0b001,
        "4.5": 0b000,
    }

    # Allowed gains
    __NAU7802_GAIN = {
        "128": 0b111,
        "64": 0b110,
        "32": 0b101,
        "16": 0b100,
        "8": 0b011,
        "4": 0b010,
        "2": 0b001,
        "1": 0b000,
    }

    # Allowed samples per second
    __NAU7802_SPS = {"320": 0b111, "80": 0b011, "40": 0b010, "20": 0b001, "10": 0b000}

    # Select between channel values
    __NAU7802_CHANNEL_1 = 0
    __NAU7802_CHANNEL_2 = 1

    # Calibration state
    __CAL_STATUS = {"SUCCESS": 0, "IN PROGRESS": 1, "FAILURE": 2}

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.exists = self.check_exists()
        self.offset_factor = None
        self.gain_factor = None

    def set_bit(self, address, value):
        """
        set register bit
        :param address:
        :param value:
        :return:
        """
        current_value = self.getU8(address)
        new_value = 0
        if current_value is not None:
            set_value = current_value | (1 << value)
            new_value = self.getU8([address, set_value])
            if new_value is not None:
                new_value = ((new_value << value) | 1) & 1
                self._logger.debug("Set bit %s at register %s", value, address)
        else:
            self._logger.warning("Failed to set bit %s at register %s", value, address)

        return new_value

    def clear_bit(self, address: int, value: int):
        """
        set register bit
        :param address:
        :param value:
        :return:
        """
        current_value = self.getU8(address)
        if current_value is not None:
            set_value = int(current_value) & ~(1 << value)
            res = self.txrx([address, set_value], readlen=1)
            if res is not None:
                return self.getU8(address)
        return None

    def get_bit(self, address: int, bit_number: int):
        """
        Read single bit from register defined by address
        :param address: Register to read
        :param bit_number: index of bit that has to be set high
        :returns: requested bit value
        """
        data = self.getU8(address)
        res = None
        if data:
            res = (data >> bit_number) & 1
        return res

    def get_serial_number(self):
        """
        A serial number is not supported by bme280
        hence a pseudo identifier is calculated by
        adding the individual calibration values together
        :returns: Pseudo-serial number
        """
        serial_number = str(self.mux_port)
        serial_number += str(self.mux.address)
        serial_number += str(self.bus.ftdi._usb_dev.serial_number)
        self._logger.info("Assigned pseudo-serial number %s", serial_number)
        return serial_number

    def check_exists(self):
        init = self.initialise()
        if init:
            self.serial_number = self.get_serial_number()
            return True
        return False

    def get_data_rdy(self):
        return bool(
            self.get_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["CR"]) == 1
        )

    def reset(self):
        self._logger.info("Reset...")
        rst = self.set_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["RR"])
        if rst is not None:
            stop_rst = self.clear_bit(
                self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["RR"]
            )
            if stop_rst is not None:
                return True
            else:
                return None
        else:
            return None

    def power_up(self):
        """
        Power up analog and digital circuit
        """
        pua_status = True

        self.set_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["PUD"])
        pud_status = self.get_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["PUD"])

        if pud_status is not None:
            self._logger.info("Power up digital successfull.")
        else:
            self._logger.warning("Digital power up failed. State:{pud_status}")
            pua_status = False

        self.set_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["PUA"])
        pua_status = self.get_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["PUA"])
        if pua_status:
            self._logger.info("Power up analog successfull.")
        else:
            self._logger.warning("Analog power up failed. State:{pud_status}")
            pua_status = False

        return pua_status

    def set_ldo_voltage(self, voltage):
        voltage = str(voltage)
        if voltage in self.__NAU7802_LDO_Voltage:
            entry = self.getU8(self.__REG["CTRL1"])
            if entry is not None:
                value = entry & 0b11000111
                value += self.__NAU7802_LDO_Voltage[voltage] << 3
                self.txrx([self.__REG["CTRL1"], value], readlen=0)
                current_voltage = self.get_ldo_voltage()
                self._logger.debug(
                    "LDO Voltage: Wrote %s (%s) Read %s",
                    voltage,
                    self.__NAU7802_LDO_Voltage[voltage],
                    current_voltage,
                )
                if current_voltage == self.__NAU7802_LDO_Voltage[voltage]:
                    self._logger.debug("Successfully set LDO Voltage: %s", value)
                    return True
                else:
                    self._logger.warning(
                        "Failed to set LDO Voltage: Set: %s \
                            Current: %s",
                        value,
                        current_voltage,
                    )
                    return False
            else:
                return False
        else:
            return False

    def get_ldo_voltage(self):
        entry = self.getU8(self.__REG["CTRL1"])
        if entry is not None:
            value = (entry >> 3) & 0b111
            self._logger.debug("Current LDO Voltage %s", value)
        return value

    def set_gain(self, gain):
        gain = str(gain)
        if gain in self.__NAU7802_GAIN:
            entry = self.getU8(self.__REG["CTRL1"])
            if entry is not None:
                value = (entry & 0b11111000) + self.__NAU7802_GAIN[gain]
                self.txrx([self.__REG["CTRL1"], value], readlen=0)
                current_gain = self.get_gain()
                if current_gain == gain:
                    return True
                else:
                    self._logger.warning(
                        "Failed to set gain: Set: %s \
                            Current: %s",
                        value,
                        current_gain,
                    )
                    return False
            else:
                return False
        else:
            return False

    def get_gain(self):
        entry = self.getU8(self.__REG["CTRL1"])
        gain = None
        if entry is not None:
            value = entry & 0b111
            self._logger.debug("Gain: %s", value)
            for k in self.__NAU7802_GAIN:
                if self.__NAU7802_GAIN[k] == value:
                    gain = k
        else:
            self._logger.warning("Failed to get gain")
        return gain

    def set_sample_rate(self, rate):
        rate = str(rate)
        if rate in self.__NAU7802_SPS:
            entry = self.getU8(self.__REG["CTRL2"])
            if entry is not None:
                self._logger.debug("CTRL2 before SPS manipulation: %d)", entry)
                value = (entry & 0b10001111) + (self.__NAU7802_SPS[rate] << 4)
                self._logger.debug("Set SPS to: %s (CTRL2: %d)", rate, value)
                self.txrx([self.__REG["CTRL2"], value], readlen=0)
                if self.get_sample_rate() == rate:
                    return True
                else:
                    self._logger.debug("Incorrect rate")
                    return False
            else:
                self._logger.debug("No response when calling CTRL2 %s", entry)
                return False
        else:
            self._logger.debug("Invalid rate: %s", rate)
            return False

    def get_sample_rate(self):
        entry = self.getU8(self.__REG["CTRL1"])
        if entry is not None:
            value = (entry | 0b0111000) >> 3
            self._logger.debug("SPS value: %s", value)
            for k in self.__NAU7802_SPS:
                if self.__NAU7802_SPS[k] == value:
                    return k
        return None

    def calibrate(self):
        """
        Initiate calibration of analog front end and wait for
        calibration to finish
        :returns: True if successfull.
        """
        calibration_state = False
        if self.begin_calibrate_afe():
            self._logger.info("Waiting for calibration to finish.")
            state = self.wait_for_calibration(10)
            if state:
                calibration_state = True
                self._logger.info("Finished calibration successfully.")
            else:
                self._logger.info("Calibration failed.")
        else:
            self._logger.error("Error initializing calibration.")
            calibration_state = False

        return calibration_state

    def begin_calibrate_afe(self):
        self._logger.info("Begin calibration of analog interface.")
        return self.set_bit(self.__REG["CTRL2"], self.__BIT["CTRL2"]["CALS"]) == 1

    def check_calibration_status(self):
        return self.getU8(self.__REG["CTRL2"]) & 0b11

    def wait_for_calibration(self, timeout_ms):
        calibration_begin = time.time()
        status = self.check_calibration_status()
        while status == self.__CAL_STATUS["IN PROGRESS"]:
            delta_time = (calibration_begin - time.time()) * 1000
            self._logger.debug("Calib status: \t %s \t %s", status, delta_time)
            if delta_time > timeout_ms:
                self._logger.error("Calibration timed out.")
                break
            status = self.check_calibration_status()
        if status == self.__CAL_STATUS["SUCCESS"]:
            return True
        else:
            return False

    def get_offset_calibration(self):
        data = [self.txrx(self.__REG["OCAL1_B2"], readlen=1)[0]]
        data += self.txrx(self.__REG["OCAL1_B1"], readlen=1)
        data += self.txrx(self.__REG["OCAL1_B0"], readlen=1)

        res = None
        if None not in data:
            res = (((data[0] << 8) + data[1]) << 8) + data[2]

        return res

    def get_gain_calibration(self):
        data = [self.txrx(self.__REG["GCAL1_B3"], readlen=1)[0]]
        data += self.txrx(self.__REG["GCAL1_B2"], readlen=1)
        data += self.txrx(self.__REG["GCAL1_B1"], readlen=1)
        data += self.txrx(self.__REG["GCAL1_B0"], readlen=1)

        res = None
        if None not in data:
            res = ((((data[0] << 8) + data[1]) << 8) + data[2]) << 8
            res += data[3]

        return res

    def enable_AVDDS(self):
        res = self.set_bit(self.__REG["PU_CTRL"], self.__BIT["PU_CTRL"]["AVDDS"])
        state = True
        if res == 0:
            self._logger.error("Failed to enable ACDDS")
            state = False
        return state

    def wait_for_conversion_cycle(self, timeout_ms):
        cycle_begin = time.time()
        status = self.get_data_rdy()
        while not status:
            delta_time = (time.time() - cycle_begin) * 1000
            self._logger.debug("Wating for conversion %s", delta_time)
            if delta_time > timeout_ms:
                time.sleep(0.01)
                self._logger.error("Conversion timed out.")
                return False
            status = self.get_data_rdy()
        return True

    def start_conversion(self):
        return self.set_bit(self.__REG["CTRL2"], self.__BIT["PU_CTRL"]["CS"])

    def prepare_measurement(self):
        self.reset()
        self.initialise()

    def initialise(self, voltage=4.5, sample_rate=320, gain=128):
        """
        Initialization procedure when NAU7802 is started
        # Power up Digital and Analog power supplies
        # First calibration run
        # Disable clock
        # Enable 330pF decoupling capacity
        # Set sample rate
        """
        init_ok = True
        # Reset all registers
        self.reset()
        # Power on analog and digital sections of the scale
        init_ok &= self.power_up()
        self._logger.info("Power up %s", init_ok)
        # Calibrate analog front end
        self.calibrate()
        self._logger.debug("Re-Calibration %s", init_ok)
        # Turn off CLK_CHP. see manual 9.1 power on sequencing
        init_ok &= self.txrx([self.__REG["ADC"], 0x30]) is not None
        self._logger.debug("Set clock frequency %s", init_ok)
        # Enable 330pF decoupling cap on chan 2.
        # see manual 9.14 application circuit note
        init_ok &= (
            self.set_bit(self.__REG["PGA_PWR"], self.__NAU7802_PGA_PWR_PGA_CAP_EN) == 1
        )
        self._logger.debug("Enable 330pF decoupling %s", init_ok)
        # Set samples per second
        init_ok &= self.set_sample_rate(sample_rate)
        self._logger.debug("Set sample rate %s", init_ok)
        self._logger.debug("PU_CTRL %s", self.getU8(self.__REG["PU_CTRL"]))
        self._logger.debug("CTRL1 %s", self.getU8(self.__REG["CTRL1"]))
        self._logger.debug("CTRL2 %s", self.getU8(self.__REG["CTRL2"]))

        # Set gain
        init_ok &= self.set_gain(gain)
        self._logger.debug("Set gain %s", init_ok)
        # Set LDO Voltage
        init_ok &= self.set_ldo_voltage(voltage)
        self._logger.debug("Set internal LDO voltage %s", init_ok)
        # Re-calibrate analog front end in case of chaning gain,
        # sample rate or channel
        init_ok &= self.calibrate()
        self._logger.debug("Re-Calibration %s", init_ok)
        # Set internal reference voltage
        init_ok &= self.enable_AVDDS()
        self._logger.debug("Enable AVDDS %s", init_ok)
        # State after initialization
        self._logger.debug("PU_CTRL %s", self.getU8(self.__REG["PU_CTRL"]))
        self._logger.debug("CTRL1 %s", self.getU8(self.__REG["CTRL1"]))
        self._logger.debug("CTRL2 %s", self.getU8(self.__REG["CTRL2"]))
        # Start conversion cycle
        self.start_conversion()
        self.offset_factor = self.get_offset_calibration()
        self.gain_factor = self.get_gain_calibration()
        return init_ok

    def get_adc(self):
        """
        Fetch data after conversion cycle has finished
        :returns: Anlog-Digital-Converter read
        """
        self.wait_for_conversion_cycle(1000)
        data = self.txrx(self.__REG["ADCO_B2"], readlen=3)
        adc = None
        if data is not None and len(data) == 3:
            adc = ((data[0] << 16) + (data[1] << 8) + data[2]) << 8
            adc = self.int32(adc)
        return adc

    def get_data(self):
        """
        Get current measurement values
        :return: data dictionary
        """
        # Wait until data is ready
        self.data = self.default_data()
        adc = None
        try:
            if self.error is None:
                adc = self.get_adc()
        except TypeError:
            # Throw an error if not able to fetch data
            self.error = Error().read(self)
            detect = self.mux.poll(self._SENSOR_ADDRESS)
            if detect:
                self._logger.warning("Sensor detected")
                self.reset()
            else:
                self._logger.error("Sensor not  detected. %s", detect)
            self.data["object"] = "ERROR"
            return self.data

        if adc is None:
            # Throw an error if not able to fetch data
            self._logger.error("Error during reading.")
            self.error = Error().read(self)
            self.mux.open_single_port(self.mux_port)
            detect = self.mux.poll(self._SENSOR_ADDRESS)
            if detect:
                self._logger.warning("Sensor detected")
                self.reset()
                init = self.initialise()
                if init:
                    self.error = None
            else:
                self._logger.error("Sensor not  detected. %s", detect)

            self.data["object"] = "ERROR"
            return self.data

        if self.error is None:
            self.data["error"] = False
            self.data["values"] = {}
            self.data["values"]["adc"] = {"value": adc, "unit": self._units["adc"]}

        return self.data
