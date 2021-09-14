# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import unittest
import logging
from pyserialsensors.core import comPortController
from pyserialsensors.core.toolbox import scan_uart

logging.basicConfig(level=logging.DEBUG)

class TestComPort(unittest.TestCase):
    def findSmg(self, ports):
        smg = None
        for port in self.ports:
            device = scan_uart(port)
            if device is not None:
                if "SMG" in device.__name__:
                    smg = device
                    break
        return smg


    def setUp(self):
        self.ports = comPortController.search_comports()

    def test_scanner(self):
        """ check if a supported comport device is connected """
        self.assertTrue(type(self.ports) == list)

    def test_scan_and_read(self):
        self.assertGreaterEqual(len(self.ports), 1)

    def test_search_device(self):
        smg_count = 0
        for port in self.ports:
            device = scan_uart(port)
            if device is not None:
                if "SMG" in device.__name__:
                    smg_count += 1
        self.assertEqual(smg_count, 1)

    def test_get_data(self):
        smg = self.findSmg(self.ports)
        smg.prepare_measurement()
        data = smg.get_data()
        self.assertIsInstance(data, dict)

        T = data["values"]["temperature"]["value"]
        self.assertLessEqual(T, 60)
        self.assertGreaterEqual(T, 0)

        P = data["values"]["abs_pressure"]["value"]
        self.assertLessEqual(P, 1e6)
        self.assertGreaterEqual(P, 1e4)

        rho = data["values"]["density"]["value"]
        self.assertLessEqual(rho, 2)
        self.assertGreaterEqual(rho, 0.5)

        m_data = smg.getMassflow()
        m_vflow = m_data[-1] / m_data[1] 
        v_vflow = data["values"]["volumeflow"]["value"]/ 6e4
        self.assertAlmostEqual(v_vflow, m_vflow, places=3)

    def test_serial_number(self):
        smg = self.findSmg(self.ports)
        sn = smg.get_serial_number()
        self.assertIsInstance(sn, str)


if __name__ == "__main__":
    TestComPort().test_get_data()
