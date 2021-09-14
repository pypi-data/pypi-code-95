# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import unittest
import logging
from ..core import comPortController
from ..core.toolbox import scan_uart
from ..devices.s8000 import S8000
import time

logging.basicConfig(level=logging.DEBUG)


class TestComPort(unittest.TestCase):
    def test_scanner(self):
        """ check if a supported comport device is connected """
        ports = comPortController.search_comports()
        self.assertTrue(type(ports) == list)

    def test_scan_and_read(self):
        ports = comPortController.search_comports()
        self.assertGreaterEqual(len(ports), 1)

    def test_search_device(self):
        ports = comPortController.search_comports()

        s8000_count = 0
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000_count += 1
        self.assertEqual(s8000_count, 1)

    def test_get_data(self):
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.prepare_measurement()
        data = s8000.get_data()
        self.assertIsInstance(data, dict)

        Tdp = data["values"]["dewpoint"]["value"]
        self.assertLessEqual(Tdp, 60)
        self.assertGreaterEqual(Tdp, -6)

        T = data["values"]["temperature"]["value"]
        self.assertLessEqual(T, 60)
        self.assertGreaterEqual(T, 0)

    def test_reconnect(self):
        """
        perform a connection loss by unplugging and repluging the device
        """
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.prepare_measurement()
        data = s8000.get_data()
        self.assertIsInstance(data, dict)
        print("Plug/Unplug the device")
        time.sleep(5)
        s8000.reconnect()

    def test_start_stop(self):
        """ Pro forma """
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.prepare_measurement()
        s8000.get_data()
        s8000.stop()
        s8000.start()
        s8000.get_data()

    def none_fct(self, *args, **kwargs):
        return None

    def test_error_on_reconnect(self):
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.get_data()
        s8000.find_port = self.none_fct
        port = s8000.reconnect()
        self.assertTrue(port is None)

    def test_sensor_exists(self):
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.prepare_measurement()
        self.assertIsInstance(s8000.sensor_exists(), str)

    def test_get_status(self):
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.prepare_measurement()
        state = s8000.STATUS()
        self.assertFalse(state["logging"])  # no logging
        self.assertTrue(state["alarm_humidity"])  # no humidity alarm

    def test_unit_register(self):
        ports = comPortController.search_comports()
        s8000 = None
        for port in ports:
            device = scan_uart(port)
            if device is not None:
                if "S8000" in device.__name__:
                    s8000 = device
                    break

        s8000.prepare_measurement()
        unit_reg = s8000.UNITSCOMMAND()
        self.assertTrue(unit_reg["language"], 0000)
