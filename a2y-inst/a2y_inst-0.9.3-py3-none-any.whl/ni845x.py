from ctypes import WinDLL as _WinDLL, c_char_p as _char_p, POINTER as _POINTER, pointer as _pointer
from ctypes import c_ulong as _ulong, c_int as _int, c_char as _char, c_uint32 as _uint32, c_uint8 as _uint8
from ctypes import c_int32 as _int32, c_uint16 as _uint16
from ctypes import byref as _byref
from typing import List as _List, Sequence as _Sequence


_dll = _WinDLL('Ni845x.dll')

_status_to_string = _dll.ni845xStatusToString
_status_to_string.argstypes = [_int32, _uint32, _char_p]
_status_to_string.restype = None


def _descript_error_code(error_code: int) -> str:
	buf = (_char * 256)()
	_status_to_string(error_code, 255, buf)
	return buf.value.decode('latin')


class Ni845Exception(Exception):
	def __init__(self, error_code: int):
		self.__error_code = error_code
		Exception.__init__(self, _descript_error_code(error_code))

	@property
	def error_code(self) -> int:
		return self.__error_code


def _err_checker(error_code: int):
	if error_code != 0:
		raise Ni845Exception(error_code)


_Handle = _ulong
_PHandle = _POINTER(_Handle)

_find_device = _dll.ni845xFindDevice
_find_device.argtypes = [_char_p, _POINTER(_ulong), _POINTER(_uint32)]
_find_device.restype = _err_checker

_open = _dll.ni845xOpen
_open.argtypes = [_char_p, _PHandle]
_open.restype = _err_checker

_close = _dll.ni845xClose
_close.argtypes = [_Handle]
_close.restype = _err_checker

_set_io_voltage_level = _dll.ni845xSetIoVoltageLevel
_set_io_voltage_level.argtypes = [_Handle, _uint8]
_set_io_voltage_level.restype = _err_checker

_i2c_set_pullup_enable = _dll.ni845xI2cSetPullupEnable
_i2c_set_pullup_enable.argtypes = [_Handle, _uint8]
_i2c_set_pullup_enable.restype = _err_checker

_i2c_configuration_open = _dll.ni845xI2cConfigurationOpen
_i2c_configuration_open.argtypes = [_PHandle]
_i2c_configuration_open.restype = _err_checker

_i2c_configuration_close = _dll.ni845xI2cConfigurationClose
_i2c_configuration_close.argtypes = [_Handle]
_i2c_configuration_close.restype = _err_checker

_i2c_configuration_get_address_size = _dll.ni845xI2cConfigurationGetAddressSize
_i2c_configuration_get_address_size.argtypes = [_Handle, _POINTER(_int32)]
_i2c_configuration_get_address_size.restype = _err_checker

_i2c_configuration_set_address_size = _dll.ni845xI2cConfigurationSetAddressSize
_i2c_configuration_set_address_size.argtypes = [_Handle, _int32]
_i2c_configuration_set_address_size.restype = _err_checker

_i2c_configuration_get_address = _dll.ni845xI2cConfigurationGetAddress
_i2c_configuration_get_address.argtypes = [_Handle, _POINTER(_uint16)]
_i2c_configuration_get_address.restype = _err_checker

_i2c_configuration_set_address = _dll.ni845xI2cConfigurationSetAddress
_i2c_configuration_set_address.argtypes = [_Handle, _uint16]
_i2c_configuration_set_address.restype = _err_checker

_i2c_configuration_get_clock_rate = _dll.ni845xI2cConfigurationGetClockRate
_i2c_configuration_get_clock_rate.argtypes = [_Handle, _POINTER(_uint16)]
_i2c_configuration_get_clock_rate.restype = _err_checker

_i2c_configuration_set_clock_rate = _dll.ni845xI2cConfigurationSetClockRate
_i2c_configuration_set_clock_rate.argtypes = [_Handle, _uint16]
_i2c_configuration_set_clock_rate.restype = _err_checker

_i2c_read = _dll.ni845xI2cRead
_i2c_read.argtypes = [_Handle, _Handle, _uint32, _POINTER(_uint32), _POINTER(_uint8)]
_i2c_read.restype = _err_checker

_i2c_write = _dll.ni845xI2cWrite
_i2c_write.argtypes = [_Handle, _Handle, _uint32, _POINTER(_uint8)]
_i2c_write.restype = _err_checker

_i2c_write_read = _dll.ni845xI2cWriteRead
_i2c_write_read.argtypes = [_Handle, _Handle, _uint32, _POINTER(_uint8), _uint32, _POINTER(_uint32), _POINTER(_uint8)]
_i2c_write_read.restype = _err_checker


class I2CConfiguration:
	def __init__(self):
		self.__handle = _Handle()
		_i2c_configuration_open(_byref(self.__handle))

	@property
	def handle(self):
		return self.__handle

	@property
	def clock_rate(self) -> int:
		value = _uint16()
		_i2c_configuration_get_clock_rate(self.__handle, _byref(value))
		return value.value

	@clock_rate.setter
	def clock_rate(self, rate: int):
		_i2c_configuration_set_clock_rate(self.__handle, rate)

	@property
	def address_size(self) -> int:
		value = _int32()
		_i2c_configuration_get_address_size(self.__handle, _byref(value))
		return value.value

	@address_size.setter
	def address_size(self, size: int):
		_i2c_configuration_set_address_size(self.__handle, size)

	@property
	def address(self) -> int:
		addr = _uint16()
		_i2c_configuration_get_address(self.__handle, _byref(addr))
		return addr.value

	@address.setter
	def address(self, addr: int):
		_i2c_configuration_set_address(self.__handle, addr)

	def close(self):
		if self.__handle.value != 0:
			_i2c_configuration_close(self.__handle)
			self.__handle.value = 0

	def __del__(self):
		self.close()


class NI845x:
	def __init__(self, device_id: str):
		self.__handle = _Handle()
		_open(device_id.encode('latin'), _byref(self.__handle))
		self.__i2c_configuration = I2CConfiguration()

	@property
	def i2c_configuration(self) -> I2CConfiguration:
		return self.__i2c_configuration

	def i2c_read(self, size: int = 1) -> _List[int]:
		assert size > 0
		buf = (_uint8 * size)()
		size_read = _uint32()
		_i2c_read(self.__handle, self.i2c_configuration.handle, size, _byref(size_read), buf)
		return buf[:size_read.value]

	def i2c_write(self, data: _Sequence):
		size = len(data)
		assert size > 0
		buf = (_uint8 * size)()
		for i in range(size):
			buf[i] = data[i]
		_i2c_write(self.__handle, self.i2c_configuration.handle, size, buf)

	def i2c_write_read(self, data_to_write: _Sequence, size_to_read: int) -> _List[int]:
		size_to_write = len(data_to_write)
		assert size_to_write > 0 and size_to_read > 0
		write_buf = (_uint8 * size_to_write)()
		for i in range(size_to_write):
			write_buf[i] = data_to_write[i]
		size_read = _uint32()
		read_buf = (_uint8 * size_to_read)()
		_i2c_write_read(
			self.__handle, self.i2c_configuration.handle,
			size_to_write, write_buf,
			size_to_read, _byref(size_read), read_buf
		)
		data = read_buf[:size_read.value]
		return data

	def enable_i2c_pullup(self, enable: bool = True):
		iv = 1 if enable else 0
		value = _uint8(iv)
		_i2c_set_pullup_enable(self.__handle, value)

	def disable_i2c_pullup(self):
		self.enable_i2c_pullup(False)

	def set_io_voltage_level(self, voltage: int):
		_set_io_voltage_level(self.__handle, voltage)

	def close(self):
		if self.__handle.value != 0:
			self.i2c_configuration.close()
			_close(self.__handle)
			self.__handle.value = 0

	def __del__(self):
		self.close()


def open_default_device() -> NI845x:
	"""
	打开系统中找到的第一个 NI845x 设备
	:return: NI845x 设备对象
	"""
	name_buffer = (_char * 260)()
	_find_device(name_buffer, None, None)
	if len(name_buffer.value) == 0:
		raise IOError('NI845x device not found.')
	return NI845x(name_buffer.value.decode('latin'))
