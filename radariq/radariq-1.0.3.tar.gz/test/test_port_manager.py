# This file is part of RadarIQ SDK
# (C) 20019 RadarIQ <support@radariq.io>
#
# SPDX-License-Identifier:    MIT

"""
Tests for the port manager module
These tests are designed to communicate with the hardware itself

"""

import unittest
import six
import radariq.port_manager as pm


class TestPortManager(unittest.TestCase):
    """ Tests for port detection """
    if six.PY2:
        assertRegex = unittest.TestCase.assertRegexpMatches  # this was renamed in python 3.2

    def test_find_com_ports(self):
        # Test that modules can be found
        response = pm.find_com_ports()
        input("Plug in 1 RadarIQ module")
        self.assertEqual(1, len(response))

    def test_find_com_port(self):
        # Test that modules can be found
        response = pm.find_com_port()
        input("Plug in 1 RadarIQ module")
        self.assertRegex(response.device, r"COM\d+")


###########################################################################


if __name__ == '__main__':
    unittest.main()
