from serial import Serial as _Serial
from typing import List as _List
from threading import Lock as _Lock


class DL_RS1A:
	ReadAllCommand = b'M0'

	def __init__(self, port: str, baudrate=9600, timeout=0.2):
		self._serial = _Serial(port=port, baudrate=baudrate, timeout=0.2)
		self._lock = _Lock()

	def _read_frame(self) -> bytes:
		return self._serial.readline()

	def _write_frame(self, frame: bytes):
		if not frame.endswith(b'\n'):
			frame += b'\r\n'
		self._serial.write(frame)

	def query(self, command: bytes) -> bytes:
		if isinstance(command, str):
			command = command.encode('latin')
		with self._lock:
			self._serial.flushInput()
			self._write_frame(command)
			line = self._read_frame()
		return line.strip()

	def read_all(self) -> _List[float]:
		line = self.query(DL_RS1A.ReadAllCommand)
		if len(line) == 0:
			raise IOError('Device response timeout.')
		if not line.startswith(DL_RS1A.ReadAllCommand):
			raise IOError('Device feedback format not valid: %s.' % line.decode('latin'))
		segments = line.split(b',')[1:]
		values = [float(seg) for seg in segments]
		return values
