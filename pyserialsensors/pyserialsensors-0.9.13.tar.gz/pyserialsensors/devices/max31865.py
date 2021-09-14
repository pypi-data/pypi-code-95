# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Sensor class for MAX31865 SPI RTD Sensor/Kelvin bridge
Based on:
https://github.com/adafruit/Adafruit_CircuitPythonself._.git
"""

import time
import logging
from pyftdi.spi import SpiIOError
from ..core.sensor import SPISensor
from pyftdi.ftdi import FtdiError


__author__ = "Konstantin Niehaus"
__copyright__ = "German Aerospace Center"
__credits__ = []
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "konstantin.niehaus@dlr.de"


class MAX31865(SPISensor):
    """Driver for the MAX31865 thermocouple amplifier."""

    __name__ = "MAX31865"

    # pylint: disable=C0326
    # Register
    _WRITE_REG = 0x80
    _CONFIG_REG = 0x00
    _CONFIG_BIAS = 0x80
    _CONFIG_MODEAUTO = 0x40
    _CONFIG_MODEOFF = 0x00
    _CONFIG_1SHOT = 0x20
    _CONFIG_3WIRE = 0x10
    _CONFIG_24WIRE = 0x00
    _CONFIG_FAULTSTAT = 0x02
    _CONFIG_FILT50HZ = 0x01
    _CONFIG_FILT60HZ = 0x00
    _RTDMSB_REG = 0x01
    _RTDLSB_REG = 0x02
    _HFAULTMSB_REG = 0x03
    _HFAULTLSB_REG = 0x04
    _LFAULTMSB_REG = 0x05
    _LFAULTLSB_REG = 0x06
    _FAULTSTAT_REG = 0x07
    _FAULT_HIGHTHRESH = 0x80
    _FAULT_LOWTHRESH = 0x40
    _FAULT_REFINLOW = 0x20
    _FAULT_REFINHIGH = 0x10
    _FAULT_RTDINLOW = 0x08
    _FAULT_OVUV = 0x04
    # pylint: enable=C0326

    # Constants
    _RTD_A = 3.9083e-3
    _RTD_B = -5.775e-7

    _units = {"temperature": "C"}

    def __init__(self, *args, rtd_nominal=100, ref_resistor=430.0, wires=4, **kwargs):
        """
        Add calibration and setup variables to instance and initializes base class
        """
        super().__init__(*args, **kwargs)

        self.ref_resistor = ref_resistor
        self.rtd_nominal = rtd_nominal
        self.serial_number = f"{self.cs+1}@{self.ftdi_serial}"
        self.wires = wires

    def setup(self):
        """
        Harware communication
        - Initialize communication bus
        - Communicate wire mode to device
        - Prepare default setup
        """
        try:
            self.device = self.bus.get_port(cs=self.cs, freq=5e6, mode=3)
        except (SpiIOError, FtdiError) as e:
            return None

        # Set wire config register based on the number of wires specified.
        if self.wires not in (2, 3, 4):
            raise ValueError("Wires must be a value of 2, 3, or 4!")

        config = self.read_u8(self._CONFIG_REG)
        if config is None:
            raise SpiIOError("Unable to read config.")
        if self.wires == 3:
            config |= self._CONFIG_3WIRE
        else:
            # 2 or 4 wire
            config &= ~self._CONFIG_3WIRE
        self.txrx(self._WRITE_REG, val=config)

        # Default to no bias and no auto conversion.
        self.bias = False
        self.auto_convert = False

    def exists(self):
        """
        Check if the sensor is available.
        """
        try:
            self.setup()
        except (SpiIOError, ValueError):
            return False
        temperature = self.temperature
        if temperature is None:
            return False
        return temperature < 500

    def get_data(self):
        """
        Fetch data from sensor and write to default data layout defined in the base class
        """
        data = self.default_data()

        try:
            self.setup()
        except SpiIOError:
            self.disconnected_ftdi = True
        else:
            data["values"] = {}
            data["values"]["temperature"] = {
                "value": self.temperature,
                "unit": self._units["temperature"],
            }
            data["error"] = False
        finally:
            return data

    @property
    def bias(self):
        """The state of the sensor's bias (True/False)."""
        return bool(self.read_u8(self._CONFIG_REG) & self._CONFIG_BIAS)

    @bias.setter
    def bias(self, val):
        config = self.read_u8(self._CONFIG_REG)
        if val:
            config |= self._CONFIG_BIAS  # Enable bias.
        else:
            config &= ~self._CONFIG_BIAS  # Disable bias.
        self.write_u8(self._WRITE_REG, config)

    @property
    def auto_convert(self):
        """The state of the sensor's automatic conversion
        mode (True/False).
        """
        return bool(self.read_u8(self._CONFIG_REG) & self._CONFIG_MODEAUTO)

    @auto_convert.setter
    def auto_convert(self, val):
        config = self.read_u8(self._CONFIG_REG)
        if val:
            config |= self._CONFIG_MODEAUTO  # Enable auto convert.
        else:
            config &= ~self._CONFIG_MODEAUTO  # Disable auto convert.
        self.write_u8(self._WRITE_REG, config)

    @property
    def fault(self):
        """The fault state of the sensor.  Use ``clear_faults()`` to clear the
        fault state.  Returns a 6-tuple of boolean values which indicate if any
        faults are present:

        - HIGHTHRESH
        - LOWTHRESH
        - REFINLOW
        - REFINHIGH
        - RTDINLOW
        - OVUV
        """
        faults = self.read_u8(self._FAULTSTAT_REG)
        highthresh = bool(faults & self._FAULT_HIGHTHRESH)
        lowthresh = bool(faults & self._FAULT_LOWTHRESH)
        refinlow = bool(faults & self._FAULT_REFINLOW)
        refinhigh = bool(faults & self._FAULT_REFINHIGH)
        rtdinlow = bool(faults & self._FAULT_RTDINLOW)
        ovuv = bool(faults & self._FAULT_OVUV)
        return (highthresh, lowthresh, refinlow, refinhigh, rtdinlow, ovuv)

    def clear_faults(self):
        """Clear any fault state previously detected by the sensor."""
        config = self.read_u8(self._CONFIG_REG)
        config &= ~0x2C
        config |= self._CONFIG_FAULTSTAT
        self.write_u8(self._CONFIG_REG, config)

    def read_rtd(self):
        """Perform a raw reading of the thermocouple and return its 15-bit
        value.  You'll need to manually convert this to temperature using the
        nominal value of the resistance-to-digital conversion and some math.  If you just want
        temperature use the temperature property instead.
        """

        self.clear_faults()
        self.bias = True
        time.sleep(0.01)
        config = self.read_u8(self._CONFIG_REG)
        if config is None:
            return None
        config |= self._CONFIG_1SHOT
        self.txrx(self._WRITE_REG, val=config)
        time.sleep(0.065)
        rtd = self.read_u16(0x01)
        if rtd is not None:
            # Remove fault bit.
            rtd >>= 1
        return rtd

    @property
    def resistance(self):
        """Read the resistance of the RTD and return its value in Ohms."""
        resistance = self.read_rtd()
        if resistance is None:
            return None
        resistance /= 32768
        resistance *= self.ref_resistor
        return resistance

    @property
    def temperature(self):
        """Read the temperature of the sensor and return its value in degrees
        Celsius.
        This math originates from:
        http://www.analog.com/media/en/technical-documentation/application-notes/AN709_0.pdf
        To match the naming from the app note we tell lint to ignore the Z1-4
        naming.
        """
        raw_reading = self.resistance
        if raw_reading is None or raw_reading == 0:
            return None
        val1 = -self._RTD_A
        val2 = self._RTD_A * self._RTD_A - (4 * self._RTD_B)
        val3 = (4 * self._RTD_B) / self.rtd_nominal
        val4 = 2 * self._RTD_B
        temp = val2 + (val3 * raw_reading)
        temp = (temp ** 0.5 + val1) / val4
        if temp > 300:
            return None
        if temp >= 0:
            return temp
        rpoly = raw_reading
        temp = -242.02
        temp += 2.2228 * rpoly
        rpoly *= raw_reading  # square
        temp += 2.5859e-3 * rpoly
        rpoly *= raw_reading  # ^3
        temp -= 4.8260e-6 * rpoly
        rpoly *= raw_reading  # ^4
        temp -= 2.8183e-8 * rpoly
        rpoly *= raw_reading  # ^5
        temp += 1.5243e-10 * rpoly
        return temp
