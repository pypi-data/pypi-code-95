# This file is part of RadarIQ SDK
# (C) 20019 RadarIQ <support@radariq.io>
#
# SPDX-License-Identifier:    MIT

"""
Tests for the RadarIQ M1 Units converter module.
"""

import unittest
import six
import radariq.units_converter as units


class TestRoundSig(unittest.TestCase):
    """ Tests for the rounding function """

    def test_sig1(self):
        """ Round a normal number to 4 sig fig"""
        rounded = units.round_sig(1.235845, 4)
        self.assertEqual(1.236, rounded)

    def test_sig2(self):
        """ Round a normal number to 0 sig fig"""
        rounded = units.round_sig(1.235845, 0)
        self.assertEqual(0, rounded)

    def test_sig3(self):
        """ Round a 0 to 1 sig fig"""
        rounded = units.round_sig(0, 1)
        self.assertEqual(0, rounded)


class TestDistanceConversions(unittest.TestCase):
    """ Tests for the distance conversions """
    if six.PY2:
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp  # this was renamed in python 3.2

    def test_convert_from_m_to_m(self):
        # Test the identity conversion
        converted = units.convert_distance_to_si('m', 1.01)
        self.assertEqual(1.01, converted)

    def test_convert_from_mm_to_m(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_to_si('mm', 1010)
        self.assertEqual(1.01, converted)

    def test_convert_from_km_to_m(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_to_si('km', 0.123)
        self.assertEqual(123, converted)

    def test_convert_from_ft_to_m(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_to_si('ft', 23)
        self.assertEqual(7.01, converted)

    def test_convert_from_mi_to_m(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_to_si('mi', 0.135)
        self.assertEqual(217.3, converted)

    def test_convert_from_m_to_ms(self):
        # Test the identity conversion
        converted = units.convert_distance_from_si('m', 1.010)
        self.assertEqual(1.01, converted)

    def test_convert_from_m_to_mm(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_from_si('mm', 1.001)
        self.assertEqual(1001, converted)

    def test_convert_from_m_to_km(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_from_si('km', 123)
        self.assertEqual(0.123, converted)

    def test_convert_from_m_to_ft(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_from_si('ft', 7.01)
        self.assertEqual(23, converted)

    def test_convert_from_m_to_mi(self):
        # Test conversions of distances to SI units
        converted = units.convert_distance_from_si('mi', 217.26)
        self.assertEqual(0.135, converted)

    def test_error_case(self):
        # Test conversion fails if bogus units are set
        with self.assertRaisesRegex(ValueError, 'Invalid units for distance conversion'):
            converted = units.convert_distance_from_si('bogus', 1)


class TestSpeedConversions(unittest.TestCase):
    """ Tests for the speed conversions """
    if six.PY2:
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp  # this was renamed in python 3.2

    def test_convert_from_meters_per_second_to_meters_per_second(self):
        # Test the identity conversion
        converted = units.convert_speed_to_si('m/s', 1.001)
        self.assertEqual(1.001, converted)

    def test_convert_from_mm_per_second_to_meters_per_second(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_to_si('mm/s', 11)
        self.assertEqual(0.011, converted)

    def test_convert_from_km_per_hour_to_meters_per_second(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_to_si('km/h', 13)
        self.assertEqual(3.611, converted)

    def test_convert_from_ft_per_second_to_meters_per_second(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_to_si('ft/s', 23)
        self.assertEqual(7.01, converted)

    def test_convert_from_mi_per_hour_to_meters_per_second(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_to_si('mi/h', 14)
        self.assertEqual(6.258, converted)

    def test_convert_from_meters_per_second_to_meters_per_second2(self):
        # Test the identity conversion
        converted = units.convert_speed_from_si('m/s', 1.001)
        self.assertEqual(1.001, converted)

    def test_convert_from_meters_per_second_to_mm_per_second(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_from_si('mm/s', 1.05)
        self.assertEqual(1050, converted)

    def test_convert_from_meters_per_second_to_km_per_hour(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_from_si('km/h', 45)
        self.assertEqual(162, converted)

    def test_convert_from_meters_per_second_to_ft_per_second(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_from_si('ft/s', 7)
        self.assertEqual(22.97, converted)

    def test_convert_from_meters_per_second_to_mi_per_hour(self):
        # Test conversions of speeds to SI units
        converted = units.convert_speed_from_si('mi/h', 21)
        self.assertEqual(46.98, converted)

    def test_error_case(self):
        # Test conversion fails if bogus units are set
        with self.assertRaisesRegex(ValueError, 'Invalid units for speed conversion'):
            converted = units.convert_speed_from_si('bogus', 1)


class TestAccelerationConversions(unittest.TestCase):
    """ Tests for the acceleration conversions """
    if six.PY2:
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp  # this was renamed in python 3.2

    def test_convert_from_meters_per_square_second_to_meters_per_square_second(self):
        # Test the identity conversion
        converted = units.convert_acceleration_to_si('m/s^2', 1.001)
        self.assertEqual(1.001, converted)

    def test_convert_from_mm_per_square_second_to_meters_per_square_second(self):
        # Test conversions of accelerations to SI units
        converted = units.convert_acceleration_to_si('mm/s^2', 11)
        self.assertEqual(0.011, converted)

    def test_convert_from_ft_per_square_second_to_meters_per_square_second(self):
        # Test conversions of accelerations to SI units
        converted = units.convert_acceleration_to_si('ft/s^2', 23)
        self.assertEqual(7.01, converted)

    def test_convert_from_meters_per_square_second_to_meters_per_square_second2(self):
        # Test the identity conversion
        converted = units.convert_acceleration_from_si('m/s^2', 1.001)
        self.assertEqual(1.001, converted)

    def test_convert_from_meters_per_square_second_to_mm_per_aquare_second(self):
        # Test conversions of accelerations to SI units
        converted = units.convert_acceleration_from_si('mm/s^2', 1.05)
        self.assertEqual(1050, converted)

    def test_convert_from_meters_per_square_second_to_ft_per_square_second(self):
        # Test conversions of accelerations to SI units
        converted = units.convert_acceleration_from_si('ft/s^2', 7)
        self.assertEqual(22.97, converted)

    def test_error_case(self):
        # Test conversion fails if bogus units are set
        with self.assertRaisesRegex(ValueError, 'Invalid units for acceleration conversion'):
            converted = units.convert_acceleration_from_si('bogus', 1)
