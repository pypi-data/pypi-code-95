# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Class extensions to associate serial device bridges,
I2C-multiplexer and I2C-sensors
"""

import logging
from pyftdi.spi import SpiController
from pyftdi.i2c import I2cController
from ..devices.MUX import TCA9548


class MUX(TCA9548):
    """
    Extend hardware MUX class such that sensors can be associtated
    """

    address = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A list of connected sensors
        self.sensors = []


class MmsI2cController(I2cController):
    """
    Extends pyftdi.i2c.I2cController such that 'MUX'
    instances can be associated
    """

    __name__ = "MmsI2cController"
    url = ""

    def __init__(self):
        super().__init__()
        # A list of multiplexer elements
        self.mux = []
        self.init = False
        if self.ftdi._usb_dev is not None:
            self._logger = logging.getLogger(
                f"{self.__name__}:{self.ftdi._usb_dev.serial_number}"
            )
        else:
            self._logger = logging.getLogger(f"{self.__name__}:Unk")

    def configure(self, url, **kwargs):
        """
        Extend pyftdi.i2c.I2cController method to
        store the FTDIs url attribute
        """
        self.url = url
        return super().configure(url, **kwargs)


class MmsSpiController(SpiController):
    """
    Extends pyftdi.Spi.SpiController
    """

    __name__ = "MmsSpiController"
    url = ""

    def __init__(self, *args, CS_MUX=False, **kwargs):

        self.CS_MUX = CS_MUX
        if self.CS_MUX:
            cs_count = 1
        else:
            cs_count = 5
        super().__init__(*args, cs_count=cs_count, **kwargs)

        self.init = False
        self.sensors = []
        if self.ftdi._usb_dev is not None:
            self._logger = logging.getLogger(
                f"{self.__name__}:{self.ftdi._usb_dev.serial_number}"
            )
        else:
            self._logger = logging.getLogger(f"{self.__name__}:Unk")

    def get_port(self, cs, freq=5e6, mode=3):
        """
        If a MUX is used between cs lines of spi
        devices and FTDI cs is set to 0 and the cs information
        is decoded into digital outputs for pins D4-D7
        """

        if self.CS_MUX:
            # Check if cs is within the correct range
            assert cs >= 0 and cs <= 15
            # Prepare SPI port
            device = super().get_port(cs=0, freq=freq, mode=mode)
            # Prepare GPIO interface
            gpio = super().get_gpio()
            # Select pins D3-D7
            pins = 0xF0
            # Set pins D3-D7 as outputs
            gpio.set_direction(pins, pins)
            # Set pins D3-D7 such that the MUX circuit
            # can forward cs to the correct device
            gpio.write(cs << 4)

        else:
            # Check if cs is within the correct range
            assert cs >= 0 and cs <= 5
            device = super().get_port(cs=cs, freq=freq, mode=mode)

        return device

    def configure(self, url, **kwargs):
        """
        Extend pyftdi.spi.SpiController method to
        store the FTDIs url attribute
        """
        self.url = url
        super().terminate()
        return super().configure(url, **kwargs)
