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
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder
from test.synchronous_server import ModbusTCPServer

test_dir = os.path.dirname(os.path.abspath(__file__))


class TestExoEdgeHoldingRegisterMethods(unittest.TestCase):
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
        self.c = lib.ExositeModbusTCP(ip_address='localhost', port=5020)
        self.pyModbusClient = ModbusTcpClient(ip_address='localhost', port=5020)
        self.expected_registers=[16,17,18,19,20,21,22,23]
        for i in range(len(self.expected_registers)):
            self.pyModbusClient.write_register(i, self.expected_registers[i])

    def tearDown(self):
        print("stopping test: {}".format(self.id().split('.')[-1]))
        self.c.client.close()
        self.pyModbusClient.close()

    def test_read_multiple_registers(self):
        eval_kwargs = {
            'data_address': 0,
            'register_count': 4,
            'byte_endianness': 'big',
            'register_endianness': 'big',
            'evaluation_mode': 'unsigned',
        }
        # register      |         00                   01                  02                 03                  04                  05                  06                  07
        # 16 bit value  |         16         |         17        |         18        |        19         |        20         |        21         |        22         |        23         |
        # binary        |0000 0000 0001 0000  0000 0000 0001 0001 0000 0000 0001 0010 0000 0000 0001 0011 0000 0000 0001 0100 0000 0000 0001 0101 0000 0000 0001 0110 0000 0000 0001 0111
        # 64 bit value  |                                   4503672642994195                             |
        expected=4503672642994195
        result = self.c.read_holding_registers(eval_kwargs)
        assert (result==expected), "Incorrect values read during a batch read"

    def test_read_register(self):
        eval_kwargs = {
            'data_address': 0,
            'register_count': 1,
            'byte_endianness': 'big',
            'register_endianness': 'big',
            'evaluation_mode': 'unsigned',
        }
        for i in range(len(self.expected_registers)):
            expected_value = self.expected_registers[i]
            eval_kwargs['data_address'] = i
            result = self.c.read_holding_registers(eval_kwargs)
            assert (result==expected_value), "Incorrect values read during a single register read"

    def test_little_endian_byte(self):
        eval_kwargs = {
            'data_address': 0,
            'register_count': 1,
            'byte_endianness': 'little',
            'register_endianness': 'big',
            'evaluation_mode': 'unsigned',
        }
        #0000.0000 0001.0000 -> 0001.0000 0000.0000
        SIXTEEN_BYTE_SWAPPED=4096
        expected_value = SIXTEEN_BYTE_SWAPPED
        result = self.c.read_holding_registers(eval_kwargs)
        assert (result==expected_value), "Incorrect values read while swapping byte endianess"

    def test_little_endian_register(self):
        eval_kwargs = {
            'data_address': 0,
            'register_count': 2,
            'register_size': 32,
            'byte_endianness': 'big',
            'register_endianness': 'little',
            'evaluation_mode': 'unsigned',
        }
        # register           |         00                   01                  02                 03                  04                  05                  06                  07
        # 16 bit value       |         16         |         17        |         18        |        19         |        20         |        21         |        22         |        23         |
        # binary             |0000 0000 0001 0000  0000 0000 0001 0001 0000 0000 0001 0010 0000 0000 0001 0011 0000 0000 0001 0100 0000 0000 0001 0101 0000 0000 0001 0110 0000 0000 0001 0111
        # little endian reg  |0000 0000 0001 0001  0000 0000 0001 0000 0000 0000 0001 0011 0000 0000 0001 0010 0000 0000 0001 0101 0000 0000 0001 0100 0000 0000 0001 0111 0000 0000 0001 0110
        # 32 bit (le) value  |              1114128                   |              1245202                  |                1376276               |                 1507350                |
        expected_val=1114128
        result = self.c.read_holding_registers(eval_kwargs)
        assert (result==expected_val), "Incorrect values read during a batch read"

    def test_larger_register(self):
        eval_kwargs = {
            'data_address': 0,
            'register_count': 2,
            'byte_endianness': 'big',
            'register_endianness': 'big',
            'evaluation_mode': 'unsigned',
        }
        # register      |         00                   01                  02                 03                  04                  05                  06                  07
        # 16 bit value  |         16         |         17        |         18        |        19         |        20         |        21         |        22         |        23         |
        # binary        |0000 0000 0001 0000  0000 0000 0001 0001 0000 0000 0001 0010 0000 0000 0001 0011 0000 0000 0001 0100 0000 0000 0001 0101 0000 0000 0001 0110 0000 0000 0001 0111
        # 32 bit value  |              1048593                   |              1179667                  |                1310741               |                 1441815                |
        #self.expected_registers_32_bit=[1048593, 1179667, 1310741, 1441815]
        self.expected_registers_32_bit=1048593

        result = self.c.read_holding_registers(eval_kwargs)
        assert (result==self.expected_registers_32_bit), "Incorrect values read during a 32bit register reads"


    def test_data_address(self):
        eval_kwargs = {
            'data_address': 2,
            'register_count': 2,
            'byte_endianness': 'big',
            'register_endianness': 'big',
            'evaluation_mode': 'unsigned',
        }
        # register      |         00                   01                  02                 03                  04                  05                  06                  07
        # 16 bit value  |         16         |         17        |         18        |        19         |        20         |        21         |        22         |        23         |
        # binary        |0000 0000 0001 0000  0000 0000 0001 0001 0000 0000 0001 0010 0000 0000 0001 0011 0000 0000 0001 0100 0000 0000 0001 0101 0000 0000 0001 0110 0000 0000 0001 0111
        # 32 bit value  |              1048593                   |              1179667                  |                1310741               |                 1441815                |
        #self.expected_registers_32_bit=[1048593, 1179667, 1310741, 1441815]
        self.expected_registers_32_bit=1179667

        result = self.c.read_holding_registers(eval_kwargs)
        assert (result==self.expected_registers_32_bit), "Incorrect values read during a 32bit register reads"

def main():
    unittest.main()

if __name__ == "__main__":
    main()
