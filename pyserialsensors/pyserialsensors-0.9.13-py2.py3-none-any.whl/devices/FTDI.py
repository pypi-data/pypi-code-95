# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
USB to I2C and SPI bridge
"""

from pyftdi.usbtools import UsbTools
from ..core.i2controller import MmsI2cController as I2cController
from ..core.i2controller import MmsSpiController as SpiController
from ..core.toolbox import scan_spi
from pyftdi.ftdi import FtdiError
import logging

# logging.basicConfig(level=logging.DEBUG)


def init_all(ftdi, CS_MUX=True):
    ftdi_devices = UsbTools.find_all(ftdi)
    bus_list = []
    serial_number = []

    for dev in ftdi_devices:
        serial_number.append(dev[0].sn)

    for dev in ftdi_devices:
        bus = None
        # Check if bus is SPI
        if unique_check(serial_number):
            bus = UM232H(dev[0].sn, CS_MUX=CS_MUX).spi()[dev[0].sn]

            scan_spi(bus)
            if len(bus.sensors) == 0:
                # If not SPI check if I2C
                try:
                    bus = UM232H(dev[0].sn).i2c()[dev[0].sn]
                except FtdiError:
                    pass
            else:
                bus.sensors = []
            bus_list.append(bus)

    return bus_list


def init_all_i2c(ftdi):
    """
    Find all supported I2C bridges and initialize the i2c interface
    """
    ftdi_devices = UsbTools.find_all(ftdi)
    i2cbus_list = {}
    serial_number = []

    for dev in ftdi_devices:
        serial_number.append(dev[0].sn)

    if unique_check(serial_number):
        for dev in ftdi_devices:
            i2cbus_list[dev[0].sn] = UM232H(dev[0].sn).i2c()[dev[0].sn]
    else:
        i2cbus_list = None

    return i2cbus_list


def init_all_spi(ftdi, CS_MUX=True):
    """
    Find all supported SPI bridges and initialize the spi interface
    :param ftdi: (VendorID, ProductID)
    """

    logger = logging.getLogger("FTDI")

    logger.debug("FTDI %s", ftdi)
    ftdi_devices = UsbTools.find_all(ftdi)
    spibus_list = {}
    serial_number = []
    logger.debug("%s bridges found.", len(ftdi_devices))

    for dev in ftdi_devices:
        serial_number.append(dev[0].sn)
        logger.debug("%s serial.", len(dev[0].sn))

    if unique_check(serial_number):
        for dev in ftdi_devices:
            spibus_list[dev[0].sn] = UM232H(dev[0].sn, CS_MUX=CS_MUX).spi()[dev[0].sn]
    else:
        spibus_list = None

    return spibus_list


def unique_check(serial_number: list):
    """
    Check if all bridges have unique identifiers
    """
    # Check if all FTDI have unique identifier
    for i in range(len(serial_number) - 1):
        for j in range(i + 1, len(serial_number)):
            if serial_number[i] == serial_number[j]:
                return False
    return True


class UM232H:
    def __init__(self, serial, **kwargs):
        """
        UM232H - USB to I2C bridge
        :param serial: [INTEGER] serial number of the UM232H chip
        :param kwargs:
            frequency: [FLOAT] communication frequency of the chip
            vendor_id: [HEX NUMBER]
            product_id: [HEX NUMBER]
            CS_MUX:[boolean] if true 4 digits are used for the communication
            to a 4 digit channel select mux. Otherwise designated cs channels
            are mapped 1 to one (up to 5)
        """
        # Either cs channels are used one to one
        # or a 4 digit digital mux is used for the cs lines
        self.serial = serial
        self.type = "UM232H"
        self.vendor_id = kwargs.get("vendor_id", None)
        self.product_id = kwargs.get("product_id", None)
        self.frequency = kwargs.get("frequency", 1e3)
        self.CS_MUX = kwargs.get("CS_MUX", False)

        self.clockstretching = True
        self.i2cbus = None
        self.spibus = None
        self.i2c_device = {}
        self.spi_device = {}

    def reset(self):
        """
        resets the I2cController
        :return:
        """
        if len(self.i2c_device) != 0:
            bus = I2cController()
            bus.configure(
                "ftdi://ftdi::" + self.serial + "/1",
                clockstretching=self.clockstretching,
                frequency=self.frequency,
            )
        elif len(self.spi_device) != 0:
            bus = SpiController()
            bus.configure(
                "ftdi://ftdi::" + self.serial + "/1",
                debug=True,
                frequency=self.frequency,
            )
        else:
            return None
        bus.flush()
        bus.terminate()

    def i2c(self):
        """
        initialises the i2c to USB bridge
        :return: [OBJECT] pyftdi bridge
        """
        self.reset()
        self.i2cbus = I2cController()
        self.i2cbus.configure(
            "ftdi://ftdi::" + self.serial + "/1",
            frequency=self.frequency,
            clockstretching=self.clockstretching,
        )
        self.i2c_device[self.serial] = self.i2cbus
        return self.i2c_device

    def spi(self):
        """
        initialises the spi to USB bridge
        :return: [OBJECT] pyftdi bridge
        """
        self.reset()
        # Instanciate a SPI controller
        self.spibus = SpiController(turbo=True, CS_MUX=self.CS_MUX)

        # Configure FTDI device as
        # SPI master
        self.spibus.configure(
            "ftdi://ftdi::" + self.serial + "/1", debug=False, frequency=self.frequency
        )
        self.spi_device[self.serial] = self.spibus

        return self.spi_device
