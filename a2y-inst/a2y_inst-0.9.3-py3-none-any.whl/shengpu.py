from serial import Serial as _Serial
from time import sleep


class SP312B(_Serial):
	"""
	盛普科技SP312B型等精度通用计数器相位计
	"""

	def __init__(self, port, continuous=False, timeout=None, baudrate=9600):
		self.continuous = continuous
		if timeout is None:
			timeout = 0.3 if continuous else 1
		_Serial.__init__(self, port, baudrate=baudrate, timeout=timeout)

	@staticmethod
	def parse_value(fb):
		unit_index = 0
		unit_char = ''
		unit_coe = 1
		for c in fb:
			if c not in '0123456789.':
				unit_char = c
				break
			unit_index += 1
		if unit_char == 'k' or unit_char == 'K':
			unit_coe = 1000
		elif unit_char == 'm':
			unit_coe = 0.001
		elif unit_char == 'M':
			unit_coe = 1000000

		try:
			return float(fb[:unit_index]) * unit_coe
		except Exception as e:
			raise ValueError('Error: Inappropriate value format from SP312B')

	def measure(self):
		self.flushInput()
		if self.continuous:
			sleep(0.05)
			if self.in_waiting > 0:
				self.readline()
			fb = self.readline()
			if fb == '':
				fb = '0.0'
		else:
			self.write(b':MEAS?\n')
			fb = self.readline().decode('utf8')
			if fb == '':
				fb = '0.0'
			elif len(fb) < 2:
				raise IOError('Error: SP312B Communication Fail')
		return SP312B.parse_value(fb)

	def set_to_frequency(self):
		self.write(b'SYST:KEY 1\n')
		if self.continuous:
			self.write(b':init:cont on\n')
