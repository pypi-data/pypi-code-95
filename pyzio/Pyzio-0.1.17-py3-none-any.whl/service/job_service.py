from typing import List

from ..pyzio_logger import PyzioLogger

from ..port.adapter.brainer_client import BrainerClient
from ..pyzio_printer import PyzioPrinter
from ..repository.local_job_repository import LocalJobRepository, Job
from ..repository.printer_state_repository import PrinterStateRepository


class JobService:

	def __init__(self,
				 printer: PyzioPrinter,
				 brainer_client: BrainerClient,
				 local_job_repo: LocalJobRepository,
				 printer_state_repo: PrinterStateRepository,
				logger: PyzioLogger):
		self._printer = printer
		self._brainer_client = brainer_client
		self._local_job_repo = local_job_repo
		self._printer_state_repo = printer_state_repo
		self._logger = logger

	def queue_jobs(self, jobs: List[Job]) -> None:
		self._local_job_repo.update_jobs(jobs)

	def start_next_job(self) -> bool:
		if not self._local_job_repo.is_queue_empty():
			self._logger.info('There are one or more jobs in the queue')
			job = self._local_job_repo.get_job_from_queue()
			self._logger.info('Fetched top job')
			printer_id, secret = self._printer_state_repo.get_printer_id(), self._printer_state_repo.get_secret()
			self._logger.info('Got secret and printer ID from the state repo')
			self._brainer_client.get_file(printer_id, secret, job)
			self._logger.info('Collected file from Brainer')
			self._printer.start_printing(job)
			return True
		self._logger.info('Printer has no job to start.')
		return False
