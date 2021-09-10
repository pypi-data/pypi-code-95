from abc import ABC, abstractmethod

from ..enums.job_status import JobStatus
from ..enums.sensor_type import SensorType


class PhasioMQTTPort(ABC):

	@abstractmethod
	def candidate_connect(self) -> None:
		pass

	@abstractmethod
	def printer_connect(self) -> None:
		pass

	@abstractmethod
	def disconnect(self) -> None:
		pass

	@abstractmethod
	def shutdown(self) -> None:
		pass

	@abstractmethod
	def set_printer_id(self, printer_id: str) -> None:
		pass

	@abstractmethod
	def get_printer_id(self) -> None:
		pass

	@abstractmethod
	def register_sensor(self, sensor_name: str, sensor_type: SensorType) -> str:
		pass

	@abstractmethod
	def stream_sensor_data(self, sensor_id: str, value: float) -> None:
		pass

	@abstractmethod
	def send_job_updates(self, job_id: str, status: JobStatus) -> None:
		pass

	@abstractmethod
	def finish_registration(self, printer_id: str) -> None:
		pass

	@abstractmethod
	def begin_listening(self) -> None:
		pass
