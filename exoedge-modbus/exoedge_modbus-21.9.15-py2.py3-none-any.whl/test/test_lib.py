# pylint: disable=C0325
import os
import errno
import unittest
import json
import time
import socket
from exoedge_modbus import lib
from exoedge.config_io import ConfigIO
from pymodbus.constants import Endian
from test.synchronous_server import ModbusTCPServer

test_dir = os.path.dirname(os.path.abspath(__file__))


class TestExoEdgeLibMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = ModbusTCPServer()
        cls.server_thread.start()
        while cls.server_thread.server != None:
            time.sleep(0.1)
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        print("tearing down suite: {}".format(cls))
        time.sleep(0.5)
        print("shutting down modbus server...")
        cls.server_thread.server.server_close()
        cls.server_thread.server.shutdown()
        print("done shutting down modbus server")

    def setUp(self):
        print("starting test: {}".format(self.id().split('.')[-1]))
        # self.ConfigIO = ConfigIO()
        # self.ConfigIO.setDaemon(True)
        # self.ConfigIO.start()
        self.c = lib.ExositeModbusTCP(ip_address='localhost', port=5020)

    def tearDown(self):
        print("stopping test: {}".format(self.id().split('.')[-1]))
        # self.ConfigIO.stop()
        self.c.client.close()

    def test_read_8_coils(self):
        self.assertTrue(True)
        eval_kwargs = {
            'data_address': 0,
            'register_count': 8,
            'byte_endianness': Endian.Little,
            'register_endianness': Endian.Little,
            'evaluation_mode': 'bitmask_bool',
            'bitmask': '0xFF',
        }
        result = self.c.read_coils(eval_kwargs)
        self.assertTrue(result)
        print(result)


def main():
    unittest.main()

if __name__ == "__main__":
    main()
