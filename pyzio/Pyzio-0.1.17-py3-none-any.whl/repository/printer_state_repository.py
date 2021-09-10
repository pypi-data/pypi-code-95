import threading
from typing import List, Tuple

from ..pyzio_settings import PyzioSettings


class PrinterStateRepository:
	def __init__(self, settings: PyzioSettings):
		self._lock = threading.Lock()
		self._settings = settings
		self._pairing_id = None
		self._pairing_code = None
		self._candidate_id = None
		self._printer_id = None
		self._secret = None
		self._sensor_ids = []

	def set_pairing_id(self, pairing_id: str) -> None:
		self._pairing_id = pairing_id

	def get_pairing_id(self) -> str:
		return self._pairing_id

	def set_candidate_id(self, candidate_id: str) -> None:
		self._candidate_id = candidate_id

	def get_candidate_id(self) -> str:
		return self._candidate_id

	def set_printer_id(self, printer_id: str) -> None:
		self._printer_id = printer_id

	def get_printer_id(self) -> str:
		return self._printer_id

	def get_sensor_ids(self) -> List[Tuple[str, str]]:
		return self._sensor_ids

	def add_sensor_id(self, phasio_id: str, external_id: str) -> None:
		self._sensor_ids.append((phasio_id, external_id))

	def load_printer(self) -> None:
		self._printer_id = self._settings.get('state.printer_id')
		self._sensor_ids = self._settings.get_sensors()
		self._secret = self._settings.get('state.secret')

	def dump_printer(self) -> None:
		with self._lock:
			self._settings.set('state.printer_id', self._printer_id)
			self._settings.set_sensors(self._sensor_ids)
			self._settings.set('state.secret', self._secret)
			self._settings.save()

	def is_printer_paired(self) -> bool:
		if self._settings.get('state.printer_id') is not None:
			return True
		else:
			return False

	def set_secret(self, secret: str) -> None:
		self._secret = secret

	def get_secret(self) -> str:
		return self._secret

	def set_pairing_code(self, pairing_code):
		self._pairing_code = pairing_code
