# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

# The MIT License (MIT)
#
# Copyright (c) 2016 Radomir Dopieralski (@deshipu),
#               2017 Robert Hammelrath (@robert-hh)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
Sensor Class for ADS1015

"""

__author__ = "Konstantin Niehaus"
__copyright__ = "German Aerospace Center"
__credits__ = ["Konstantin Niehaus", "Radomir Dopieralski", "Rober Hammelrath"]
__license__ = ""
__version__ = "0.1.0"
__email__ = "konstantin.niehaus@dlr.de"

from ..core.sensor import I2CSensor
from ..core.error import Error

_REGISTER_MASK = 0x03
_REGISTER_CONVERT = 0x00
_REGISTER_CONFIG = 0x01
_REGISTER_LOWTHRESH = 0x02
_REGISTER_HITHRESH = 0x03

_OS_MASK = [0x80, 0x00]
_OS_SINGLE = [0x80, 0x00]  # Write: Set to start a single-conversion
_OS_BUSY = [0x00, 0x00]  # Read: Bit=0 when conversion is in progress
_OS_NOTBUSY = [0x80, 0x00]  # Read: Bit=1 when no conversion is in progress

_MUX_MASK = [0x70, 0x00]
_MUX_DIFF_0_1 = [0x00, 0x00]  # Differential P  =  AIN0, N  =  AIN1 (default)
_MUX_DIFF_0_3 = [0x10, 0x00]  # Differential P  =  AIN0, N  =  AIN3
_MUX_DIFF_1_3 = [0x20, 0x00]  # Differential P  =  AIN1, N  =  AIN3
_MUX_DIFF_2_3 = [0x30, 0x00]  # Differential P  =  AIN2, N  =  AIN3
_MUX_SINGLE_0 = [0x40, 0x00]  # Single-ended AIN0
_MUX_SINGLE_1 = [0x50, 0x00]  # Single-ended AIN1
_MUX_SINGLE_2 = [0x60, 0x00]  # Single-ended AIN2
_MUX_SINGLE_3 = [0x70, 0x00]  # Single-ended AIN3

_PGA_MASK = [0x0E, 0x00]
_PGA_6_144V = [0x00, 0x00]  # +/-6.144V range  =  Gain 2/3
_PGA_4_096V = [0x02, 0x00]  # +/-4.096V range  =  Gain 1
_PGA_2_048V = [0x04, 0x00]  # +/-2.048V range  =  Gain 2 (default)
_PGA_1_024V = [0x06, 0x00]  # +/-1.024V range  =  Gain 4
_PGA_0_512V = [0x08, 0x00]  # +/-0.512V range  =  Gain 8
_PGA_0_256V = [0x0A, 0x00]  # +/-0.256V range  =  Gain 16

_MODE_MASK = [0x01, 0x00]
_MODE_CONTIN = [0x00, 0x00]  # Continuous conversion mode
_MODE_SINGLE = [0x01, 0x00]  # Power-down single-shot mode (default)

_DR_MASK = [0x00, 0xE0]  # Values ADS1015/ADS1115
_DR_128SPS = [0x00, 0x00]  # 128 /8 samples per second
_DR_250SPS = [0x00, 0x20]  # 250 /16 samples per second
_DR_490SPS = [0x00, 0x40]  # 490 /32 samples per second
_DR_920SPS = [0x00, 0x60]  # 920 /64 samples per second
_DR_1600SPS = [0x00, 0x80]  # 1600/128 samples per second (default)
_DR_2400SPS = [0x00, 0xA0]  # 2400/250 samples per second
_DR_3300SPS = [0x00, 0xC0]  # 3300/475 samples per second
_DR_860SPS = [0x00, 0xE0]  # -   /860 samples per Second

_CMODE_MASK = [0x00, 0x10]
_CMODE_TRAD = [0x00, 0x00]  # Traditional comparator with hysteresis (default)
_CMODE_WINDOW = [0x00, 0x10]  # Window comparator

_CPOL_MASK = [0x00, 0x08]
_CPOL_ACTVLOW = [0x00, 0x00]  # ALERT/RDY pin is low when active (default)
_CPOL_ACTVHI = [0x00, 0x08]  # ALERT/RDY pin is high when active

_CLAT_MASK = [0x00, 0x04]  # Determines if ALERT/RDY pin latches once asserted
_CLAT_NONLAT = [0x00, 0x00]  # Non-latching comparator (default)
_CLAT_LATCH = [0x00, 0x04]  # Latching comparator

_CQUE_MASK = [0x00, 0x03]
_CQUE_1CONV = [0x00, 0x00]  # Assert ALERT/RDY after one conversions
_CQUE_2CONV = [0x00, 0x01]  # Assert ALERT/RDY after two conversions
_CQUE_4CONV = [0x00, 0x02]  # Assert ALERT/RDY after four conversions
# Disable the comparator and put ALERT/RDY in high state (default)
_CQUE_NONE = [0x00, 0x03]

_GAINS = (
    _PGA_6_144V,  # 2/3x
    _PGA_4_096V,  # 1x
    _PGA_2_048V,  # 2x
    _PGA_1_024V,  # 4x
    _PGA_0_512V,  # 8x
    _PGA_0_256V,  # 16x
)

_GAINS_V = (
    6.144,  # 2/3x
    4.096,  # 1x
    2.048,  # 2x
    1.024,  # 4x
    0.512,  # 8x
    0.256,  # 16x
)

_CHANNELS = {
    (0, None): _MUX_SINGLE_0,
    (1, None): _MUX_SINGLE_1,
    (2, None): _MUX_SINGLE_2,
    (3, None): _MUX_SINGLE_3,
    (0, 1): _MUX_DIFF_0_1,
    (0, 3): _MUX_DIFF_0_3,
    (1, 3): _MUX_DIFF_1_3,
    (2, 3): _MUX_DIFF_2_3,
}

_RATES = (
    _DR_128SPS,  # 128/8 samples per second
    _DR_250SPS,  # 250/16 samples per second
    _DR_490SPS,  # 490/32 samples per second
    _DR_920SPS,  # 920/64 samples per second
    _DR_1600SPS,  # 1600/128 samples per second (default)
    _DR_2400SPS,  # 2400/250 samples per second
    _DR_3300SPS,  # 3300/475 samples per second
    _DR_860SPS,  # - /860 samples per Second
)


class ADS1015(I2CSensor):
    """
    Analog digital converter ADS1015
    """

    __name__ = "ADS1015"
    _units = {
        "dU01": "V",
    }

    _SENSOR_ADDRESS = 0x48
    sensor_type = __name__
    _i2c_freq = 40e4
    mode = 0

    def __init__(self, *args, gain: int = 1, **kwargs):
        """
        :param gain:
        """
        super().__init__(*args, **kwargs)
        self.gain = gain
        self.exists = self.sensor_exists()
        self.temp2 = bytearray()

    def sensor_exists(self):
        """
        test if sensor is plugged in and works proper
        :return: [BOOLEAN] True if test was successful otherwise False
        """
        serial_number = self.get_serial_number()

        exists = False
        if isinstance(serial_number, str) and serial_number != "":
            exists = True
            self.serial_number = serial_number
        else:
            self.error = "No connection."
            exists = False
        return exists

    def get_serial_number(self):
        """
        Generate Pseudo serial number
        :return: [STRING] not supported
        :raises: Warning
        """
        try:
            raw = self.read(channel1=0, channel2=1)
            assert isinstance(raw, bool) == False
            assert abs(self.raw_to_v(raw)) < 100
            return f"ADS{self.mux_port}@{self.ftdi_serial}"
        except AssertionError:
            return False

    def raw_to_v(self, raw):
        """ convert raw data to voltage """
        res = None
        if raw is not None:
            v_p_b = _GAINS_V[self.gain] / 32767.0
            res = raw * v_p_b
        return res

    def set_conv(self, rate: int = 4, channel1: int = 0, channel2=None):
        """Set mode for read_rev"""
        self.mode = _CQUE_NONE
        param = [
            _CLAT_NONLAT,
            _CPOL_ACTVLOW,
            _CMODE_TRAD,
            _RATES[rate],
            _MODE_SINGLE,
            _OS_SINGLE,
            _GAINS[self.gain],
            _CHANNELS[(channel1, channel2)],
        ]

        for par in param:
            for i, coef in enumerate(par):
                self.mode[i] |= coef

    def read(self, rate=4, channel1=0, channel2=None):
        """Read voltage between a channel and GND.
        Time depends on conversion rate."""
        param = [
            _CLAT_NONLAT,
            _CPOL_ACTVLOW,
            _CMODE_TRAD,
            _RATES[rate],
            _MODE_SINGLE,
            _OS_SINGLE,
            _GAINS[self.gain],
            _CHANNELS[(channel1, channel2)],
        ]
        cmd = _CQUE_NONE
        for par in param:
            for i, coef in enumerate(par):
                cmd[i] = cmd[i] | coef
        # ba = self.txrx([_REGISTER_CONVERT], readlen=2)
        # self.txrx([_REGISTER_CONFIG, cmd[0], cmd[1]], readlen=0)
        data = self.txrx([_REGISTER_CONVERT], readlen=2)

        if data is not None:
            res = (data[0] << 8) | data[1]
            if res > 32768:
                res -= 65536
        else:
            res = None

        return res

    def get_data(self):
        """
        Acquire data from sensor and return result physical values
        """
        self.error = None
        self.data = self.default_data()

        try:
            raw = self.read(channel1=0, channel2=1)
        except TypeError:
            # Throw an error if not able to fetch data
            self.mux.close_all_ports()
            self.error = Error().read(self)
            self.data["object"] = "ERROR"
            return self.data

        if self.error is None:
            val = self.raw_to_v(raw)
            if val is not None and val < 100:
                self.data["error"] = False
                self.data["values"] = {}
                self.data["values"]["dU01"] = {
                    "value": val,
                    "unit": self._units["dU01"],
                }
            else:
                self.error = Error().read(self)
                self.prepare_measurement()
                self.data["object"] = "ERROR"
            return self.data

    def read_rev(self):
        """Read voltage between a channel and GND. and then start
        the next conversion."""
        raw_data = self.txrx([_REGISTER_CONVERT], readlen=2)
        self.txrx([_REGISTER_CONFIG, self.mode[0], self.mode[1]], readlen=0)
        res = (raw_data[0] << 8) | raw_data[1]
        return res if res < 32768 else res - 65536

    def alert_start(
        self,
        rate=4,
        channel1=0,
        channel2=None,
        threshold_high=0x4000,
        threshold_low=0,
        latched=False,
    ):
        """Start continuous measurement, set ALERT pin on threshold."""
        self.txrx([_REGISTER_LOWTHRESH, threshold_low], readlen=0)
        self.txrx([_REGISTER_HITHRESH, threshold_high], readlen=0)
        self.txrx(
            [
                _REGISTER_CONFIG,
                _CQUE_1CONV | _CLAT_LATCH
                if latched
                else _CLAT_NONLAT
                | _CPOL_ACTVLOW
                | _CMODE_TRAD
                | _RATES[rate]
                | _MODE_CONTIN
                | _GAINS[self.gain]
                | _CHANNELS[(channel1, channel2)],
            ],
            readlen=0,
        )

    def conversion_start(self, rate=4, channel1=0, channel2=None):
        """Start continuous measurement, trigger on ALERT/RDY pin."""
        self.txrx([_REGISTER_LOWTHRESH, 0], readlen=0)
        self.txrx([_REGISTER_HITHRESH, 0x8000], readlen=0)
        self.txrx(
            [
                _REGISTER_CONFIG,
                _CQUE_1CONV
                | _CLAT_NONLAT
                | _CPOL_ACTVLOW
                | _CMODE_TRAD
                | _RATES[rate]
                | _MODE_CONTIN
                | _GAINS[self.gain]
                | _CHANNELS[(channel1, channel2)],
            ],
            readlen=0,
        )

    def alert_read(self):
        """Get the last reading from the continuous measurement."""
        res = self.txrx([_REGISTER_CONVERT], readlen=3)
        return res if res < 32768 else res - 65536
