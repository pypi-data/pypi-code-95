from abc import ABC, abstractmethod
from typing import List, Tuple


class PyzioSettings(ABC):
	@abstractmethod
	def get(self, name: str) -> str:
		pass

	@abstractmethod
	def get_sensors(self) -> List[Tuple[str, str]]:
		pass

	@abstractmethod
	def set_sensors(self, sensors: List[Tuple[str, str]]) -> None:
		pass

	@abstractmethod
	def set(self, name: str, value: str) -> None:
		pass

	@abstractmethod
	def save(self) -> None:
		pass

	@abstractmethod
	def print_file_storage(self) -> str:
		pass
