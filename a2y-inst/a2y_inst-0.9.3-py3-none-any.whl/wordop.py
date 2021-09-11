from serial import Serial as _Serial
from threading import Lock as _Lock
from time import sleep as _sleep


class DigitalController:
	Head = b'\x40'

	@staticmethod
	def calc_crc(*args):
		crc = 0
		for arg in args:
			for seg in arg:
				crc += seg
		return crc % 256

	def __init__(self, port: str, baudrate=19200, timeout=0.5):
		self.__controller = _Serial(port=port, baudrate=baudrate, timeout=timeout)
		self.__lock = _Lock()
		self.__device_type: int = 1
		self.__device_id: int = 0
		self.__try_count = 1
		self.__try_interval = 1
		self.__communication_fail_count = 0

	@property
	def timeout(self) -> float:
		return self.__controller.timeout

	@timeout.setter
	def timeout(self, value: float):
		self.__controller.timeout = value

	@property
	def communication_fail_count(self) -> int:
		return self.__communication_fail_count

	@property
	def try_count(self) -> int:
		return self.__try_count

	@try_count.setter
	def try_count(self, value: int):
		assert isinstance(value, int)
		assert value > 0

	@property
	def try_interval(self) -> float:
		return self.__try_interval

	@try_interval.setter
	def try_interval(self, value: float):
		assert isinstance(value, (int, float))
		assert value > 0

	@property
	def device_type(self) -> int:
		return self.__device_type

	@device_type.setter
	def device_type(self, value: int):
		assert isinstance(value, int)
		assert 0 <= value <= 255
		self.__device_type = value

	@property
	def device_id(self) -> int:
		return self.__device_id

	@device_id.setter
	def device_id(self, value: int):
		assert isinstance(value, int)
		assert 0 <= value <= 255
		self.__device_id = value

	def __recv_frame_body(self):
		head = self.__controller.read()
		while len(head) == 1 and head != DigitalController.Head:
			head = self.__controller.read()
		if len(head) != 1:
			raise IOError('Read frame head timeout.')
		length = self.__controller.read()
		if len(length) != 1:
			raise IOError('Read data length timeout.')
		body = self.__controller.read(length[0])
		if len(body) != length[0]:
			raise IOError('Read frame body timeout.')
		crc = self.__controller.read()
		if len(crc) != 1:
			raise IOError('Read CRC timeout.')

		crc1 = DigitalController.calc_crc(head, length, body)
		if crc[0] != crc1:
			raise IOError('CRC incorrect.')

		return body

	def __send_frame_body(self, body):
		length = bytearray([len(body)])
		crc = DigitalController.calc_crc(DigitalController.Head, length, body)
		self.__controller.write(DigitalController.Head)
		self.__controller.write(length)
		self.__controller.write(body)
		self.__controller.write(bytearray([crc]))

	def __query(self, body):
		with self.__lock:
			self.__controller.flushInput()
			for i in range(self.try_count):
				self.__send_frame_body(body)
				try:
					feedback = self.__recv_frame_body()
				except Exception as e:
					if i < self.try_count:
						_sleep(self.try_interval*(i+1))
					else:
						self.__communication_fail_count += 1
						raise e
				else:
					break
		return feedback

	def write_something(self, body):
		feedback = self.__query(body)
		assert len(feedback) == 3
		if feedback[2] != 0:
			raise IOError('Configure device failed.')

	def read_something(self, body):
		return self.__query(body)

	def set_light_strength(self, strength: int, channel: int = 0):
		assert 0 <= strength < 256
		body = bytearray([self.__device_type, self.__device_id, 0x1A, channel, strength])
		self.write_something(body)

	def close(self):
		self.__controller.close()

	def open(self):
		self.__controller.open()

	@property
	def is_open(self) -> bool:
		return self.__controller.is_open
