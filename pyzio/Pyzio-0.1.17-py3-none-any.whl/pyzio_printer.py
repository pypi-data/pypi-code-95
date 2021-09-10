from abc import ABC, abstractmethod

from .domain.job import Job


class PyzioPrinter(ABC):
	@abstractmethod
	def start_printing(self, job: Job) -> None:
		pass

	@abstractmethod
	def delete_file_from_storage(self, path: str) -> None:
		pass

	@abstractmethod
	def register_sensor(self, sensor_name: str, phasio_sensor_id: str) -> None:
		pass

	@abstractmethod
	def printer_name(self) -> str:
		pass

	@abstractmethod
	def printer_model(self) -> str:
		pass

	@abstractmethod
	def printer_material(self) -> str:
		pass
