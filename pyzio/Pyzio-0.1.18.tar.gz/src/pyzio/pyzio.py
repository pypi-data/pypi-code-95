from .service.update_service import UpdateService
from typing import Tuple, List

from .config.brainer_config import BrainerConfig
from .config.mqtt_topics_config import MQTTTopicsConfig
from .enums.job_status import JobStatus
from .enums.sensor_type import SensorType
from .port.adapter.brainer_client import BrainerClient
from .port.adapter.phasio_mqtt_adapter import PhasioMQTTAdapter
from .pyzio_listener import PyzioListener
from .pyzio_logger import PyzioLogger
from .pyzio_printer import PyzioPrinter
from .pyzio_settings import PyzioSettings
from .repository.local_job_repository import LocalJobRepository
from .repository.printer_state_repository import PrinterStateRepository
from .service.job_service import JobService
from .service.printer_service import PrinterService


class Pyzio(PyzioListener):

	def __init__(self, logger: PyzioLogger, listener: PyzioListener, printer: PyzioPrinter, settings: PyzioSettings):
		self._listener = listener
		self._logger = logger
		self._printer = printer
		self._settings = settings
		self._mqtt_config = MQTTTopicsConfig(settings)
		self._brainer_config = BrainerConfig(settings)

		self._printer_state_repo = PrinterStateRepository(settings)
		self._local_job_repo = LocalJobRepository(logger)
		self._brainer_client = BrainerClient(self._brainer_config)
		self._job_service = JobService(self._printer, self._brainer_client, self._local_job_repo, self._printer_state_repo, self._logger)
		self._update_service = UpdateService()
		self._printer_service = PrinterService(self._printer_state_repo)
		self._phasio_port = PhasioMQTTAdapter(self._logger, self._job_service, self._update_service, self._mqtt_config, self._printer_service, self)

	def initialise_printer(self):
		if not self._printer_service.is_printer_paired():
			pairing_code, candidate_id, secret = self._brainer_client.register_candidate(self._printer.printer_name(),
																						 self._printer.printer_model(),
																						 self._printer.printer_material())
			self._printer_service.set_secret(secret)
			self.on_pairing_code_generated(pairing_code)
			self.on_candidate_registered(candidate_id)
			self._phasio_port.candidate_connect()
			self._phasio_port.listen_for_printer_id()

		else:
			self._printer_service.load_printer()
			self._phasio_port.printer_connect()
			self._phasio_port.begin_listening()

	def get_printer_id(self):
		return self._printer_service.get_printer_id()

	def get_pairing_id(self):
		return self._printer_service.get_pairing_id()

	def get_candidate_id(self):
		return self._printer_service.get_candidate_id()

	def set_printer_id(self, printer_id):
		return self._printer_service.set_printer_id(printer_id)

	def set_pairing_code(self, pairing_code):
		return self._printer_service.set_pairing_code(pairing_code)

	def set_candidate_id(self, candidate_id):
		return self._printer_service.set_candidate_id(candidate_id)

	def on_candidate_registered(self, candidate_id: str):
		self._printer_service.set_candidate_id(candidate_id)
		self._listener.on_candidate_registered(candidate_id)

	def on_pairing_code_generated(self, pairing_code: str) -> None:
		self._listener.on_pairing_code_generated(pairing_code)

	def on_printer_registered(self, printer_id: str):
		self._printer_service.dump_printer()
		self._phasio_port.begin_listening()
		self._listener.on_printer_registered(printer_id)

	def listen_for_sensor_ids(self):
		self._phasio_port.listen_for_sensor_ids()

	def on_sensor_registered(self, sensor_id: str, request_id: str):
		self._listener.on_sensor_registered(sensor_id, request_id)

	def on_job_received(self) -> None:
		self._listener.on_job_received()

	def on_markready_received(self) -> None:
		self._listener.on_markready_received()

	def register_sensor(self, sensor_name: str, sensor_type: SensorType) -> str:
		return self._phasio_port.register_sensor(sensor_name, sensor_type)

	def get_sensor_mappings(self) -> List[Tuple[str, str]]:
		return self._printer_state_repo.get_sensor_ids()

	def add_sensor_mappings(self, sensor_name: str, sensor_id: str) -> None:
		self._printer_state_repo.add_sensor_id(sensor_id, sensor_name)
		self._printer_state_repo.dump_printer()

	def start_next_job(self) -> bool:
		return self._job_service.start_next_job()

	def mark_job_failed(self, job_id: str):
		self._local_job_repo.add_job_to_failed_list(job_id)
		self._phasio_port.send_job_updates(job_id, status=JobStatus.FAILED)

	def mark_job_complete(self, job_id: str, filepath: str):
		self._local_job_repo.add_job_to_completed_list(job_id)
		self._printer.delete_file_from_storage(filepath)
		self._phasio_port.send_job_updates(job_id, status=JobStatus.COMPLETED)

	def mark_job_inprogress(self, job_id: str):
		self._phasio_port.send_job_updates(job_id, status=JobStatus.IN_PROGRESS)

	def send_sensor_update(self, sensor_id: str, value: float):
		self._phasio_port.stream_sensor_data(sensor_id, value)

	def shutdown(self):
		self._phasio_port.shutdown()
		self._logger.info('Disconnected from the Broker')
		self._settings.save()

	def on_update_command_received(self) -> None:
		self._logger.info('update command received')
