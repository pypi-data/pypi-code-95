# talk to honeywell temperature monitor
from __future__ import absolute_import, unicode_literals, print_function, division
import threading
import six
from random import normalvariate
if not six.PY3:
    from pymodbus.constants import Endian
    from pymodbus.payload import BinaryPayloadDecoder
    from pymodbus.client.sync import ModbusTcpClient as ModbusClient
else:
    from pymodbus3.constants import Endian
    from pymodbus3.payload import BinaryPayloadDecoder
    from pymodbus3.client.sync import ModbusTcpClient as ModbusClient


class MinitrendError(Exception):
    pass


class Minitrend:
    def __init__(self, address, port):
        self.address = address
        self.client = ModbusClient(address, port=port)
        # list mapping pen ID number to address
        self.pen_addresses = {i: 0x18C0 + i*0x2 for i in range(16)}
        self.alarm_addresses = {i: 0x1980 + i*0x1 for i in range(16)}
        self.unit_id = 0x01  # allows us to address different units on the same network
        # thread safe access
        self._lock = threading.Lock()

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        self.client.close()

    def connect(self):
        success = self.client.connect()
        return success

    def read_register(self, address, size):
        """
        Get a payload from a register

        Raises
        ------
        MinitrendError
            When reading fails
        """
        with self._lock:
            try:
                payload = self.client.read_input_registers(address, size, unit=self.unit_id)
            except Exception as err:
                raise MinitrendError(str(err))
        return payload

    def get_pen(self, pen_number):
        address = self.pen_addresses[pen_number]
        result = self.read_register(address, 2)
        if not six.PY3:
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                         endian=Endian.Big)
        else:
            decoder = BinaryPayloadDecoder.from_registers(result.registers,
                                                          endian=Endian.Big)
        return decoder.decode_32bit_float()

    def get_alarm(self, alarm_number):
        address = self.alarm_addresses[alarm_number]
        result = self.read_register(address, 1)
        if not six.PY3:
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                         endian=Endian.Big)
        else:
            decoder = BinaryPayloadDecoder.from_registers(result.registers,
                                                          endian=Endian.Big)
        value = decoder.decode_16bit_uint()
        # six alarms, each corresponding to a bit of the return value
        flags = [(value >> i) & 1 for i in range(6)]
        return flags


class MinitrendEmulator:

    def __init__(self, pen_values, noise_level=0):
        self.pen_values = pen_values
        self.noise_level = noise_level

    def connect(self):
        return True

    def disconnect(self):
        return

    def get_pen(self, pen_number):
        return self.pen_values + self.noise_level * normalvariate(0, 1)

    def get_alarm(self, alarm_number):
        return [0, 0, 0, 0, 0, 0]
