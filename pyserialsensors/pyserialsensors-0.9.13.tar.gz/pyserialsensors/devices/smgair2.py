# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Class to open SMGair measurement device
Inlcudes all RS232 functions referenced in the manual for SMG Air 2
"""

import serial
from serial.tools import list_ports
import struct
import time
import termios
import logging
from ..core.sensor import UARTSensor
from ..core.error import Error
import binascii
import struct

import timeout_decorator

# logging.basicConfig(level=logging.INFO)


class SMGair2(UARTSensor):
    """Serial interface for SMGair2. All commands sent are taken from
    the :download:`SMGair2.0 documentation<smgair_rs232.pdf>`.

    :param str port: Path to port i.e. */dev/ttyUSB0*

    If no or an incorrect port was given, a warning will be displayed.
    The instance will not be closed in order to make further tests possible.
    """

    __name__ = "SMGair2"
    _serial_mode = "COM"
    _units = {
        "abs_pressure": "Pa",
        "density": "kg/m3",
        "temperature": "°C",
        "volumeflow": "m3/s",
    }
    _log = None
    _max_waiting_time = 0.5  # [s]

    def __init__(self, port, scan=False, delay=0.01):
        # Check if SMG device can be opened
        self.delay = delay  # time delay between measurements [i]
        self.SMG = self.openSMG(port)
        self.port = port
        if not scan:
            self._log = logging.getLogger(name=str(self))
            self.serial_number = self.get_serial_number()
            self.ftdi_serial = "NaN"

    def __str_(self):
        return f"{self.__name__}@{self.port}"

    def reconnect(self):
        port = self.find_port(self.ftdi_serial)
        if port is None:
            return None

        self.port = port
        try:
            self.openSMG(self.port)
        except serial.serialutil.SerialException:
            if self._log is not None:
                self._log.warning("Failed to reconnect.")

    def openSMG(self, port):
        """Open SMGAir device using baudarte, bytesize, parity and stopbits
        given in :download:`SMGair2.0 documentation<smgair_rs232.pdf>`

        :param str port: Path to port i.e. /dev/ttyUSB0
        :returns: serial.Serial instance
        """
        SMG = serial.Serial(
            port=port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        if SMG.isOpen():
            SMG.close()
        SMG.open()
        return SMG

    def getMSG(self, op):
        """Compile message for SMG device

        :param bytes op: hexadecimal serial command i.e. ``0x01``
        :returns: serial message
        :rtype: 3x1 array of bytes
        """

        msg = [0xAA, op, 0x00]
        msg.append(self.checkSum(msg))
        return bytearray(msg)

    # Get information about the SMGAir 2 deivce used
    def getDeviceInfo(self, stdout=False):
        """Get information about the used device

        :param bool stdout: If ``true`` device information will be written
        to stdout. (default ``false``)
        :returns: serial number, device number, hardware version,
        software version and usage data
        :rtype: list
        """

        sn = self.getSN()  # serial number
        ID = self.getID()  # device number
        vers_HW = self.getVersionHW()  # hardware version
        vers_FW = self.getVersionFM()  # firmware version
        usage = self.getUsageData()  # usage statistics
        if stdout:  # stdout of device information
            print("_" * 40)
            print("Device information:")
            print("> Serial no.:\t\t" + sn)
            print("> Device ID:\t\t" + ID)
            print("> Hardware ver.:\t" + vers_HW)
            print("> Firmware ver.:\t" + vers_FW)
        #        sn = sn.replace("\x00", "")
        #        ID = ID.replace("\x00", "")
        #        vers_HW = vers_HW.replace("\x00", "")
        #        vers_FW = vers_FW.replace("\x00", "")
        return [sn, ID, vers_HW, vers_FW, usage]

    def getVolflow(self, stdout=False):
        """Returns absolute pressure [Pa], fluid density [kg/m^3],
        temperature [°C] and volume flow[m^3/s]

        :param bool stdout: If ``true`` recorded physical quantities
        will be written to stdout. (default ``false``)
        """
        msg = self.getMSG(0x01)
        data = self.txrx(msg)
        # for testing purposes
        # extract values from received data
        pabs = self.convert2value(data[0:4])  # abs. pressure [Pa]
        rho = self.convert2value(data[4:8])  # Density [kg/m**3]
        temp = self.convert2value(data[8:12]) - 273.15  # Temperature [°C]
        vflow = self.convert2value(data[12:16]) * 60000  # Volume flow[l/min]

        if stdout:
            print("_" * 40)
            print("Current values (volume):")
            print("> Abs. pressure:\t{:6d} Pa".format(int(pabs)))
            print("> Density:\t\t{:6.4f} kg/m^3".format(rho))
            print("> Temperature\t\t{:6.2f} °C".format(temp))
            print("> Volume flow\t\t{:6.4f} m^3/s".format(vflow))

        return [pabs, rho, temp, vflow]

    def getNorm(self, stdout=False):
        """Returns used normalization type.

        =====  =====
        value  norm
        =====  =====
        0      density
        1      pressure
        =====  =====

        :param bool stdout: If ``true`` normalization type will be written
        to stdout. (default ``false``)
        :returns: normalization pressure [Pa], normalization temperature [°C]
        and normalization type
        :rtype: ndarray
        """

        msg = self.getMSG(0x05)
        data = self.txrx(msg)
        pnorm = self.convert2value(data[0:4])  # abs. pressure [Pa]
        tnorm = self.convert2value(data[4:8])  # Density [kg/m**3]
        N = data[8:12]  # Temperature [°C]
        normtype = 0
        for n in N:
            normtype = n
        if stdout:
            print("_" * 40)
            print("Normalization parameters:")
            print("> Norm pressure:\t{:6d} Pa".format(int(pnorm)))
            print("> Norm temperature:\t{:6.2f} °C".format(tnorm))
            if normtype == 1:
                print("> Norm type:\t Pressure")
            elif normtype == 0:
                print("> Norm type: \t\tDensity")
            else:
                print("Value error in norm parameter")
        return [pnorm, tnorm, normtype]

    def getID(self):
        """Reads device ID

        :returns: device ID
        :rtype: int
        """
        msg = self.getMSG(0x06)
        return self.txrx(msg)

    def getVersionHW(self):
        """Reads hardware version

        :returns: hardware version number
        :rtype: str
        """
        msg = self.getMSG(0x08)
        return self.txrx(msg)

    def getVersionFM(self):
        """Reads firmware version

        :returns: firmware version number
        :rtype: str
        """
        msg = self.getMSG(0x09)
        return self.txrx(msg)

    def getUsageData(self):
        """Reads usage data

        :returns: total volume flow [kg], volume flow since last reset [kg],
        operating hours
        :rtype: list
        """
        msg = self.getMSG(0x0B)
        data = self.txrx(msg)
        counter_tot = self.convert2value(data[0:8])  # total counter [kg]
        counter_tot_rst = self.convert2value(data[8:16])  # resetable counter [kg]

        oph = int.from_bytes(data[16:20], "little") / 100

        return [counter_tot, counter_tot_rst, oph]

    def getSN(self):
        """Reads serial number

        :returns: serial number
        :rtype: int
        """
        msg = self.getMSG(0x07)
        sn = self.txrx(msg)
        while 0x00 in sn:
            sn = sn[:-1]
        return sn.decode("utf-8")

    def txrx(self, msg):
        """
        Sending ``msg`` to serial port and reading answer.
        The first three bytes are read.
        The third contains information about how many bytes will follow.
        The exact amount of data will then be read to ``data``.
        After data was received a delay defined in ``self.dt`` is
        implemented to prevent communication errors.

        :returns: reveived data from serial port
        :rtype: byte array
        """
        self.SMG.write(msg)
        head = self.SMG.read(3)
        n_databytes = head[2]
        data = self.SMG.read(n_databytes + 1)[:-1]
        time.sleep(self.delay)
        return data

    def sensor_exists(self):
        try:
            serial_number = self.get_serial_number()

        except StopIteration:
            if self._log is not None:
                selfSMG._log.info("Stop iteration.")
            self.SMG.close()
            return None

        if self._log is not None:
            self._log.info(f"Sensor serial: {serial_number}")

        self.SMG.close()
        return serial_number

    def prepare_measurement(self):
        try:
            self.openSMG(self.port)
        except serial.serialutil.SerialException:
            if self._log is not None:
                self._log.error("Failed to start")
            return None
        info = self.getDeviceInfo()

    def get_data(self):
        self.data = self.default_data()
        raw = self.getVolflow()
        if raw is not None:
            self.data["values"] = {}
            self.data["values"]["abs_pressure"] = {
                "value": raw[0],
                "unit": self._units["abs_pressure"],
            }
            self.data["values"]["density"] = {
                "value": raw[1],
                "unit": self._units["density"],
            }
            self.data["values"]["temperature"] = {
                "value": raw[2],
                "unit": self._units["temperature"],
            }
            self.data["values"]["volumeflow"] = {
                "value": raw[3],
                "unit": self._units["volumeflow"],
            }
            self.data["error"] = False
            return self.data

        self.error = Error().read(self)
        self.prepare_measurement()
        return self.error

    @timeout_decorator.timeout(0.5, timeout_exception=StopIteration)
    def get_serial_number(self):
        info = self.getDeviceInfo()
        serial_number = info[0]
        return serial_number

    def getMassflow(self, stdout=False):
        msg = self.getMSG(0x02)
        data = self.txrx(msg)

        # extract values from received data
        pabs = self.convert2value(data[0:4])  # abs. pressure [Pa]
        rho = self.convert2value(data[4:8])  # Density [kg/m**3]
        temp = self.convert2value(data[8:12]) - 273.15  # Temperature [K]
        mflow = self.convert2value(data[12:16])  # Mass flow [kg/s]

        if stdout:
            print("_" * 40)
            print("Current values (mass):")
            print("> Abs. pressure:\t{:6d} Pa".format(int(pabs)))
            print("> Density:\t\t{:6.4f} kg/m^3".format(rho))
            print("> Temperature\t\t{:6.2f} K".format(temp))
            print("> Mass flow\t\t{:6.4f} kg/s".format(mflow))
        return [pabs, rho, temp, mflow]

    # calcluate checksum
    def checkSum(self, msg):
        csum = 0x00
        for m in msg:
            csum = csum ^ m
        return csum

    def start(self):
        self.SMG = self.openSMG(self.port)

    # read 4 element hex array to float following IEEE754
    def convert2value(self, data):
        raw = ""
        if len(data) == 4:
            # conversion to float
            val = struct.unpack("f", data)[0]
        else:
            # conversion to uin
            val = struct.unpack("<d", data)[0]

        return val
