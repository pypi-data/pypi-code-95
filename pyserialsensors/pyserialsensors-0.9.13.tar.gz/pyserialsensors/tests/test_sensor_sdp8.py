# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import unittest
from unittest.mock import MagicMock
import logging
from ..core.i2controller import MmsI2cController
from ..core.toolbox import scan_i2c
from ..devices.FTDI import init_all
from ..core.error import Error
from ..devices.sdp.sdp8xx import SDP8XX

logging.basicConfig(level=logging.DEBUG)


class I2CSensor:
    sensor = None

    def setUp(self):
        supported_converters = [(0x0403, 0x6014)]
        self.dev = init_all(supported_converters)
        self.sensor = self.search_device()

    def test_scan_and_read(self):
        self.assertGreaterEqual(len(self.dev), 1)

    def search_device(self):
        sensor_count = 0
        for dev in self.dev:
            scan_i2c(dev)
        for dev in self.dev:
            if dev is None:
                continue
            if dev.mux is None:
                continue
            for mux in dev.mux:
                if mux.sensors is None:
                    continue
                for sensor in mux.sensors:
                    if self.sensor_type in sensor["obj"].sensor_type:
                        sensor_count += 1
                        sensor = sensor["obj"]
        self.assertGreaterEqual(sensor_count, 1)
        return sensor


class PhysicalTestSDP8xx(I2CSensor, unittest.TestCase):
    sensor_type = "SDP8"

    def test_measurement(self):
        prepared = self.sensor.prepare_measurement()
        self.assertTrue(prepared)
        data = self.sensor.get_data()
        self.assertEqual(data["object"], "DATA")
        self.assertGreater(data["values"]["temperature"]["value"], -10)
        self.assertGreater(100, data["values"]["temperature"]["value"])

    def test_failing_measurement(self):
        self.sensor.get_raw_data = MagicMock(return_value=None)
        prepared = self.sensor.prepare_measurement()
        self.assertIsInstance(prepared, dict)
        self.assertTrue(prepared["object"], "ERROR")
        self.assertTrue(prepared["error_type"], "read")


class MockTestSDP8xx(unittest.TestCase):
    sensor_type = "SDP8"

    def setUp(self):
        bus = MagicMock()
        mux = MagicMock()
        mux.__str__ = "DummyMUX"
        mux.address = 0x00
        self.sensor = SDP8XX(bus, mux, 0x01)

    def test_processing_of_valid_data(self):
        self.assertTrue(self.sensor is not None)

        # 0 Values
        data_sets = [
            # Null reading
            [[0x00, 0x00, 0x00, 0x00, 0x00, 0x01], 0, 0],
            # Max negative reading, uniform pressure scaling
            [[0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01], round(-1 / 200.0, 2), -1],
            # Min negative reading, pressure factor 8
            [[0x80, 0x00, 0x80, 0x00, 0x00, 0x08], -163.84, -(2 ** 12)],
            # Max positive reading, pressure factor 8
            [
                [0x7F, 0xFF, 0x7F, 0xFF, 0x00, 0x02],
                round(0x7FFF / 200.0, 2),
                round(0x7FFF / 2, 3),
            ],
        ]
        for data in data_sets:
            raw = data[0]
            T = data[1]
            dp = data[2]
            N = len(raw)
            for i in range(int(N / 2)):
                crc = Error.checksum(raw[i * 3 : i * 3 + 2], 0xFF)[0]
                raw.insert(i * 3 + 2, crc)

            self.sensor.txrx = MagicMock(return_value=raw)

            data = self.sensor.get_data()

            self.assertIsInstance(data, dict)
            self.assertFalse(data["error"])
            self.assertEqual(data["values"]["temperature"]["value"], T)
            self.assertEqual(data["values"]["diff_pressure"]["value"], dp)

    def test_processing_of_invalid_crc(self):
        data_sets = [
            # Invalid first crc
            [0x00, 0x00, 0x00] + [0x00, 0x01, 176] * 2,
            # Invalid second crc
            [0x00, 0x00, 0x80] + [0x00, 0x00, 0x00] + [0x00, 0x01, 176],
            # Invalid third crc
            [0x00, 0x00, 0x80] * 2 + [0x00, 0x01, 0x08],
            # All crc invalid
            [0x00, 0x01, 175] * 3,
        ]
        for data in data_sets:
            self.sensor.txrx = MagicMock(return_value=data)
            data = self.sensor.get_data()
            self.assertIsInstance(data, dict)
            self.assertEqual(data["object"], "ERROR")

    def test_processing_of_scaling(self):
        # Zero pressure scale
        raw = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        N = len(raw)
        for i in range(int(N / 2)):
            crc = Error.checksum(raw[i * 3 : i * 3 + 2], 0xFF)[0]
            raw.insert(i * 3 + 2, crc)

        self.sensor.txrx = MagicMock(return_value=raw)
        data = self.sensor.get_data()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["object"], "ERROR", data)

    def test_incomplete_reading(self):
        self.sensor.prepare_measurement = MagicMock(return_value=True)
        self.sensor.reset = MagicMock(return_value=True)

        # Zero pressure scale
        raw = [0x12] * 8

        self.sensor.txrx = MagicMock(return_value=raw)
        data = self.sensor.get_data()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["object"], "ERROR", data)

        # Zero pressure scale
        raw = [0x12] * 10
        self.sensor.txrx = MagicMock(return_value=raw)
        data = self.sensor.get_data()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["object"], "ERROR", data)

    def test_sensor_support(self):
        self.sensor.prepare_measurement = MagicMock(return_value=True)
        self.sensor.reset = MagicMock(return_value=True)

        raw = [
            0x03,
            0x02,
            0xCE,
            0x0B,
            0x01,
            0xAA,
            0x00,
            0x00,
            0x81,
            0x00,
            0x00,
            0x81,
            0x73,
            0xEF,
            0x78,
            0xAD,
            0xD4,
            0xFE,
        ]
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), int)

        # First CRC invalid
        raw[2] += 1
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "CRC")
        # Frist and second CRC invalid
        raw[5] += 1
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "CRC")
        # Second CRC invalid
        raw[2] -= 1
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "CRC")
        # CRC valid but unkown sensor type
        self.sensor.crc_check = MagicMock(return_value=[True] * 6)
        raw[0] += 10
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "InvalidSensor")

    def test_reset(self):
        self.sensor.txrx = MagicMock(side_effect=IOError)
        rst = self.sensor.reset()
        self.assertFalse(rst)

    def test_sensor_exists(self):
        self.sensor.get_serial_number = MagicMock(return_value=False)
        exists = self.sensor.sensor_exists()
        self.assertFalse(exists)

    def test_sensor_serial(self):
        self.sensor.prepare_measurement = MagicMock(return_value=True)
        self.sensor.reset = MagicMock(return_value=True)
        # Valid data

        raw = [
            0x03,
            0x02,
            0xCE,
            0x0B,
            0x01,
            0xAA,
            0x00,
            0x00,
            0x81,
            0x00,
            0x00,
            0x81,
            0x73,
            0xEF,
            0x78,
            0xAD,
            0xD4,
            0xFE,
        ]
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), int)

        # Third crc invalid
        raw[8] += 1
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "CRC")

        # All crc invalid
        raw[11] += 1
        raw[14] += 2
        raw[17] -= 1
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "CRC")

        # Incomplete data
        raw[8] -= 1
        raw = raw[:9]
        self.sensor.get_raw_serial = MagicMock(return_value=raw)
        self.assertIsInstance(self.sensor.get_serial_number(), dict)
        self.assertEqual(self.sensor.get_serial_number()["error_type"], "read")
