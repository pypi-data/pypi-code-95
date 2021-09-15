# pylint: disable=C0325,C0103,C1801
import os
import errno
import time
import unittest
import threading
import json
from test.synchronous_server import ModbusTCPServer
from exoedge.config_io import ConfigIO
from exoedge_modbus import lib
from murano_client.client import MuranoClient

test_dir = os.path.dirname(os.path.abspath(__file__))


class TestReadWriteCoils(unittest.TestCase):
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
        cls.server_thread.server.server_close()
        cls.server_thread.server.shutdown()

    def setUp(self):
        test_name = self.id().split('.')[-1]
        print("setting up for test: {}".format(test_name))
        config_io_file = os.path.join(test_dir, 'assets', test_name+'.json')
        config_io_json = json.load(open(config_io_file, 'r'))
        device = MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            )
        device.start_client()
        self.ConfigIO = ConfigIO(
            device=device,
            config_io= config_io_json)
        # self.ConfigIO.setDaemon(False)
        self.ConfigIO.start()

    def tearDown(self):
        print("stopping test: {}".format(self.id().split('.')[-1]))
        self.ConfigIO.stop()

    def test_001_1_holding_coil(self):

        start = time.time()
        print('###################\n\n\n'*3 + "channels: {}".format(self.ConfigIO.channels))
        for name, channel in self.ConfigIO.channels.items():
            print(name, channel)
            data = channel.q_out.get(timeout=5.0)
            print("data: {}".format(data))
            self.assertIsInstance(data[1], bool)


    def test_002_1_holding_register_from_exosense(self):

        start = time.time()
        print('###################\n\n\n'*3 + "channels: {}".format(self.ConfigIO.channels))
        for name, channel in self.ConfigIO.channels.items():
            print(name, channel)
            data = channel.q_out.get(timeout=5.0)
            print("data: {}".format(data))
            self.assertIsInstance(data[1], int)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
