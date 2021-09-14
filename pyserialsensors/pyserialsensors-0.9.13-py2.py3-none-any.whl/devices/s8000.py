# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT
# https://unix.stackexchange.com/questions/67936/attaching-usb-serial-device-with-custom-pid-to-ttyusb0-on-embedded

import minimalmodbus
import time
from ..core.sensor import UARTSensor
from serial.tools import list_ports
import timeout_decorator
import logging


class S8000(UARTSensor):
    __name__ = "S8000"
    _serial_mode = "COM"
    __supported_sensors = ["S8000"]
    _units = {
        "dewpoint": "°C",
        "temperature": "°C",
    }
    _log = None
    _max_waiting_time = 0.5  # [s]
    __max_attempts = 2

    _COMMANDS = {
        # Register map definition   Address[dec] Register config.
        "INSTID": [0, "H"],
        "HUMIDITY": [1, "N2"],
        "AMBTEMP": [3, "N2"],
        "RH": [5, "A"],
        "PRESSURE": [6, "J"],
        "PPMV": [7, "N2"],
        "PPMWSF": [9, "N2"],
        "GM3_HI": [11, "N2"],
        "GKG": [13, "N2"],
        "FLOW_RATE": [15, "H"],
        "MIRROR_COND": [16, "J"],
        "HP_DRIVE": [17, "H"],
        "STATUS": [18, "D"],
        "DCC_HOLD_TIME": [
            19,
            "KMM",
        ],  # K register, two realtive times, [minute, minute]
        "MEASURE_TIME": [20, "KHM"],  # K register, relative time, hour, minute
        "PHASE_TIME_HRS": [21, "H"],
        "PHASE_TIME_MIN_SEC": [22, "KMS"],  # K register, relative time, minute, second
        "FILM_THICKNESS": [23, "A"],
        "LIVE_FILM_THICKNESS": [24, "A"],
        "MAX_MA1": [25, "M"],
        "MIN_MA1": [26, "M"],
        "MAX_MA2": [27, "M"],
        "MIN_MA2": [28, "M"],
        "MAX_MA3": [29, "M"],
        "MIN_MA3": [30, "M"],
        "OP_SELECTION1": [31, "B1"],
        "OP_SELECTION2": [32, "B2"],
        "LOG_INTERVAL": [33, "H"],
        "UNITSCOMMAND": [34, "E"],
        "MIRROR_TEMP_SETP": [35, "M"],
        "EMITTERDRIVE": [36, "H"],
        "STABILITY_TIME": [37, "H"],
        "YEARMONTH": [
            38,
            "KYm",
        ],  # [not working] K register, absolute time, year, month
        "DATEHRS": [39, "KDH"],  # [not working] K register, absolute time, date, hour
        "MINSSECS": [
            40,
            "KMS",
        ],  # [not working] K register, absolute time, minute, second
        "DISPLAY_SETTING1": [41, "F"],
        "DISPLAY_SETTING2": [42, "F"],
        "FILENAME_DDMM": [46, "KmD"],  # [not working]
        "FILENAME_HHMM": [47, "KHM"],  # [not working]
        "FIRM_VER": [48, "A"],
        "ALARMCONFIG_DISPCONT": [52, "P"],
        "PROCESSALARM_SP_HI": [53, "M"],
    }

    def __init__(self, port, scan=False, DEBUG=False):
        self.DEBUG = DEBUG
        # Set serial parameters (see manual appendix D.3)
        self.port = port
        self.dev = self.connect()

        self.__maxAttempts = 10
        if not scan:
            self._log = logging.getLogger(name=str(self))
            self.serial_number = self.get_serial_number()
            self.ftdi_serial = self.get_ftdi_serial()

    def connect(self):
        dev = minimalmodbus.Instrument(self.port, 1, debug=self.DEBUG)
        dev.serial.baudrate = 9600
        dev.serial.bytesize = 8
        dev.serial.parity = minimalmodbus.serial.PARITY_NONE
        dev.serial.stopbits = 2
        dev.serial.timeout = 1
        return dev

    def reconnect(self):
        port = self.find_port(self.ftdi_serial)
        if port is None:
            return None

        self.port = port

        # try:
        self.dev = self.connect()
        # except serial.serialutil.SerialException:
        #    if self._log is not None:
        #        self._log.warning("Failed to reconnect.")

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
            if serial_number == "undefined":
                return None
        except StopIteration:
            if self._log is not None:
                self._log.info("Stop iteration.")
            return None

        if self._log is not None:
            self._log.info(f"Sensor serial: {serial_number}")

        return serial_number

    def start(self):
        self.read_values()

    def prepare_measurement(self):
        self._log = logging.getLogger(name=str(self))
        self.serial_number = self.get_serial_number()
        self.ftdi_serial = self.get_ftdi_serial()
        self.start()

    def stop(self):
        pass

    def get_data(self):
        data = self.read_values()
        if data is None:
            if self._log is not None:
                self._log.error("Error fetching values.")
        time.sleep(1)
        return data

    def read_values(self):
        self.data = self.default_data()
        dewpoint = self.HUMIDITY()
        T = self.AMBTEMP()
        if T == 120:
            T = None

        self.data["values"] = {}
        self.data["values"]["dewpoint"] = {
            "value": dewpoint,
            "unit": self._units["dewpoint"],
        }
        self.data["values"]["temperature"] = {
            "value": T,
            "unit": self._units["temperature"],
        }

        self.data["error"] = False
        return self.data

    @timeout_decorator.timeout(5, timeout_exception=StopIteration)
    def get_serial_number(self):
        test = self.HUMIDITY()
        if test is not None:
            return self.get_ftdi_serial()

    def __str__(self):
        return f"S8000@{self.port}"

    def __getattr__(self, attr):
        return lambda *args: self.cmd(attr, *args)

    def cmd(self, arg):
        if arg in self._COMMANDS.keys():
            n = 0
            time.sleep(0.6)
            while n < self.__maxAttempts:
                try:
                    if self._COMMANDS[arg][1] == "A":
                        r = (
                            self.dev.read_register(self._COMMANDS[arg][0], signed=True)
                            / 100.0
                        )
                    elif self._COMMANDS[arg][1] == "N2":
                        # get number of consecutive registers to be used for
                        # IEEE 754 float calculation
                        r = self.dev.read_float(
                            self._COMMANDS[arg][0], number_of_registers=2
                        )
                    elif self._COMMANDS[arg][1] == "D":
                        BA = self.dev.read_register(self._COMMANDS[arg][0])
                        ba = f"{BA:016b}"
                        r = {}
                        r["reset_optics_reset"] = ba[0] == "1"
                        r["hold_disply"] = ba[1] == "1"
                        r["init_maxcool"] = ba[2] == "1"
                        r["init_dcc"] = ba[3] == "1"
                        r["logging"] = ba[4] == "1"
                        r["fast"] = ba[5] == "1"
                        r["alarm_fault"] = ba[6] == "1"
                        r["alarm_humidity"] = ba[7] == "1"
                        r["external_prt"] = ba[8] == "1"
                        r["init_standby"] = ba[9] == "1"
                        r["heating"] = ba[10] == "1"
                        r["cooling"] = ba[11] == "1"
                        r["standby"] = ba[12] == "1"
                        r["maxcool"] = ba[13] == "1"
                        r["hold"] = ba[14] == "1"
                        r["dcc"] = ba[15] == "1"

                    elif self._COMMANDS[arg][1] == "E":
                        BA = self.dev.read_register(self._COMMANDS[arg][0])
                        ba = f"{BA:016b}"
                        r = {}
                        r["language"] = ba[:4]
                        r["reset2default"] = ba[4]
                        r["fast_enable"] = ba[5]
                        r["unit_Tdp"] = ba[6:8]
                        r["unit_p"] = ba[10:12]
                        r["standby"] = ba[12]
                        r["maxcool"] = ba[13]
                        r["hold"] = ba[14]
                        r["dcc"] = ba[15]

                    elif self._COMMANDS[arg][1] == "H":
                        r = self.dev.read_register(self._COMMANDS[arg][0], signed=False)
                    elif self._COMMANDS[arg][1] == "J":
                        r = (
                            self.dev.read_register(self._COMMANDS[arg][0], signed=False)
                            / 10.0
                        )
                    elif self._COMMANDS[arg][1][0] == "K":
                        spec = self._COMMANDS[arg][1][1:]
                        r = self.dev.read_register(self._COMMANDS[arg][0])
                        # Convert to Binary coded decimal [BCD]
                        ba = [r >> 8, r & 0xFF]
                        ba[0] = f"{ba[0]:2x}"
                        ba[1] = f"{ba[1]:2x}"

                        # Assign identifier to values
                        r = []

                        # distinguish absolute and relative times
                        identifier = {
                            "S": "sec",
                            "M": "min",
                            "H": "hour",
                            "D": "day",
                            "m": "month",
                            "Y": "year",
                        }
                        for i, s in enumerate(spec):
                            r.append({identifier[spec[i]]: ba[i]})

                    elif self._COMMANDS[arg][1][0] == "M":
                        r = self.dev.read_register(self._COMMANDS[arg][0], signed=True)

                    elif self._COMMANDS[arg][1][:2] in ["B1", "B2"] or self._COMMANDS[
                        arg
                    ][1][0] in ["F", "P", "L"]:
                        """ Not supported. Feel free to add this"""
                        r = None

                    return r
                except (
                    minimalmodbus.NoResponseError,
                    minimalmodbus.InvalidResponseError,
                ) as e:
                    n += 1
                    time.sleep(1)
