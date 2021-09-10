from typing import List, Tuple

from .generic_config import GenericConfig


class StateConfig(GenericConfig):

	def printer_id(self) -> str:
		return self.get_required_property('state.printer_id')

	def candidate_id(self) -> str:
		return self.get_required_property('state.candidate_id')

	def pairing_id(self) -> str:
		return self.get_required_property('state.pairing_id')

	def sensor_ids(self) -> List[Tuple[str, str]]:
		return self.sensor_ids()
