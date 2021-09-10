from .generic_config import GenericConfig


class BrainerConfig(GenericConfig):

	def host(self) -> str:
		return self.get_required_property('brainer.base_url')

	def file_storage(self) -> str:
		return self._settings.print_file_storage()
