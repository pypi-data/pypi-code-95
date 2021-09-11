from a2y_modbus import Master as _Modbus
from serial import Serial as _Serial
from threading import Lock as _Lock


class XCPlc:
	def __init__(self, port: str, baudrate: int = 115200):
		self._serial = _Serial(port, baudrate, timeout=0.3)
		self.__modbus = _Modbus(self._serial, timeout=0.3)
		self.__lock = _Lock()

	def set_coil(self, station: int, name: str, value: bool):
		coil_type = name[0]
		if coil_type == 'Y':
			start_address = 0x4800
		else:
			raise TypeError(f'Coil type "{coil_type}" is not supported yet.')
		shift = int(name[1:], 8)
		with self.__lock:
			self.__modbus.write_coil(station=station, address=start_address + shift, value=value)

	def set_uint16(self, station: int, name: str, value: int):
		num_start_idx = -1
		for idx, char in enumerate(name):
			if str.isdigit(char):
				num_start_idx = idx
				break
		assert num_start_idx > 0
		register_type = name[:num_start_idx]
		address = int(name[num_start_idx:])
		if register_type != 'D':
			raise TypeError(f'Register type "{register_type}" is not supported yet.')

		with self.__lock:
			self.__modbus.write_uint16(station, address, value)
