from typing import List, Tuple

from ..repository.printer_state_repository import PrinterStateRepository


class PrinterService:

	def __init__(self, printer_state_repo: PrinterStateRepository):
		self._printer_state_repo = printer_state_repo

	def load_printer(self) -> None:
		self._printer_state_repo.load_printer()

	def dump_printer(self) -> None:
		self._printer_state_repo.dump_printer()

	def is_printer_paired(self) -> bool:
		return self._printer_state_repo.is_printer_paired()

	def get_sensor_ids(self) -> List[Tuple[str, str]]:
		return self._printer_state_repo.get_sensor_ids()

	def add_sensor_id(self, phasio_id: str, external_id: str) -> None:
		return self._printer_state_repo.add_sensor_id(phasio_id, external_id)

	def get_printer_id(self) -> str:
		return self._printer_state_repo.get_printer_id()

	def set_printer_id(self, printer_id: str) -> None:
		return self._printer_state_repo.set_printer_id(printer_id)

	def get_candidate_id(self) -> str:
		return self._printer_state_repo.get_candidate_id()

	def set_candidate_id(self, candidate_id: str) -> None:
		return self._printer_state_repo.set_candidate_id(candidate_id)

	def get_pairing_id(self) -> str:
		return self._printer_state_repo.get_pairing_id()

	def set_pairing_id(self, pairing_id: str) -> None:
		return self._printer_state_repo.set_pairing_id(pairing_id)

	def set_secret(self, secret: str) -> None:
		return self._printer_state_repo.set_secret(secret)

	def get_secret(self) -> str:
		return self._printer_state_repo.get_secret()

	def set_pairing_code(self, pairing_code):
		return self._printer_state_repo.set_pairing_code(pairing_code)
