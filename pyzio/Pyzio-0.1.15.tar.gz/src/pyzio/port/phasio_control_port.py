from abc import ABC, abstractmethod

from ..domain.job import Job


class PhasioControlPort(ABC):

	@abstractmethod
	def get_file(self, printer_id: str, secret: str, job: Job) -> str:
		pass

	@abstractmethod
	def register_candidate(self, job_id: str, filename: str, cluster_id: str) -> (int, str, str):
		pass
