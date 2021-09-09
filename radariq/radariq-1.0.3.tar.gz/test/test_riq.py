# This file is part of RadarIQ SDK
# (C) 2019 RadarIQ <support@radariq.io>
#
# SPDX-License-Identifier:    MIT

"""
Some tests for the RadarIQ API wrapper.
These tests use a mock pyserial implementation.
"""

import unittest
import logging
import six
from radariq.RadarIQ import RadarIQ

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)


class TestMethods(unittest.TestCase):
    """ Tests for the API wrapper """
    if six.PY2:
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp  # this was renamed in python 3.2

    def setUp(self):
        self.riq = RadarIQ(port="COM3")

    def test_messages(self):
        try:
            text = '1|255|Test message'
            msg = b'\xff\x02\x01' + text.ljust(200, '\x00').encode()
            self.riq.connection.send_bsl_packet(msg)
            self.riq._read()
        except:
            pass

    def test_get_version(self):
        # Test the version command
        response = self.riq.get_version()
        self.assertEqual("Firmware: 1.0.2 Hardware: 3.0.5", response)

    def test_get_serial_number(self):
        # Test the version command
        response = self.riq.get_serial_number()
        self.assertEqual("88888-99999", response)

    def test_reset(self):
        # Test the reset command
        response = self.riq.reset(0)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Invalid reset code'):
            self.riq.reset(9)

    def test_get_frame_rate(self):
        # Test getting the frame rate
        response = self.riq.get_frame_rate()
        self.assertEqual(10, response)

    def test_set_frame_rate(self):
        # Test setting the frame rate
        response = self.riq.set_frame_rate(1)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Frame rate must be an integer'):
            self.riq.set_frame_rate(1.5)
        with self.assertRaisesRegex(ValueError, 'Frame rate must be between 0 and 30 fp'):
            self.riq.set_frame_rate(40)

    def test_get_mode(self):
        # Test getting the mode
        response = self.riq.get_mode()
        self.assertEqual(1, response)

    def test_set_mode(self):
        # Test setting of a mode
        response = self.riq.set_mode(1)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Invalid mode'):
            self.riq.set_mode(9)

    def test_get_distance_filter(self):
        # Test the filter distance command
        response = self.riq.get_distance_filter()
        self.assertEqual(response, {'minimum': 0, 'maximum': 10})

    def test_set_distance_filter(self):
        # Test the filter distance command
        # These are set in meters because that is the default
        response = self.riq.set_distance_filter(0, 2.01)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Distance filter minimum must be a number between 0 and 10000'):
            self.riq.set_distance_filter(-1, 1)

        with self.assertRaisesRegex(ValueError, 'Distance filter maximum must be a number between 0 and 10000'):
            self.riq.set_distance_filter(1, 99)

        with self.assertRaisesRegex(ValueError, 'Distance filter minimum must be a number between 0 and 10000'):
            self.riq.set_distance_filter(99, 1)

    def test_get_angle_filter(self):
        # Test getting the angle filter
        response = self.riq.get_angle_filter()
        self.assertEqual(response, {'minimum': -55, 'maximum': 55})

    def test_set_angle_filter(self):
        # Test setting the angle filter
        response = self.riq.set_angle_filter(-40, 50)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Angle filter maximum must be an integer between \-55 and \+55'):
            self.riq.set_angle_filter(0, 100)

        with self.assertRaisesRegex(ValueError, 'Angle filter minimum must be an integer between \-55 and \+55'):
            self.riq.set_angle_filter(-100, 10)

    def test_get_moving_filter(self):
        # Test getting the moving filter
        response = self.riq.get_moving_filter()
        self.assertEqual(0, response)

    def test_set_moving_filter(self):
        # Test setting of a mode
        response = self.riq.set_moving_filter(0)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Moving filter value is invalid'):
            self.riq.set_moving_filter(9)

    def test_save(self):
        # Test the save function
        response = self.riq.save()
        self.assertIs(True, response)

    def test_get_point_density(self):
        # Test getting the angle filter
        response = self.riq.get_point_density()
        self.assertEqual(0, response)

    def test_set_point_density(self):
        # Test setting the point density
        response = self.riq.set_point_density(0)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Invalid point density setting'):
            self.riq.set_point_density(5)

    def test_get_certainty(self):
        # Test getting the certainty
        response = self.riq.get_certainty()
        self.assertEqual(5, response)

    def test_set_certainty(self):
        # Test setting the certainty
        response = self.riq.set_certainty(5)
        self.assertIs(True, response)

        with self.assertRaisesRegex(ValueError, 'Certainty must be an integer between 1 and 10'):
            self.riq.set_certainty(55)

    def test_capture(self):
        # Test data capture
        self.riq.start()
        while True:
            data = self.riq.get_data(1000)
            if data is not None:
                break
        self.assertIsNotNone(data)
        self.riq.stop()

###########################################################################


if __name__ == '__main__':
    unittest.main()
