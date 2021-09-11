"""
深圳市誉恒达科技有限公司产品驱动
"""
from serial import Serial as _Serial
from threading import Thread as _Thread
from time import sleep as _sleep
from typing import Union as _Union


class M300:
	"""
	M300 条码扫码枪驱动
	"""
	def __init__(self, port: str, baudrate: int = 9600, *args, **kwargs):
		self.__serial = _Serial(port, baudrate, *args, **kwargs)
		self.__listening = False
		self.__stop_flag = False
		self.__scan_thread: _Union[_Thread, None] = None

	def __scan_function(self):
		while not self.__stop_flag:
			if self.__listening:
				self.__serial.flushInput()
