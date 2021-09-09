from ..pyzio_settings import PyzioSettings


class GenericConfig:
	def __init__(self, settings: PyzioSettings):
		# TODO: Check data that's being loaded meets the schema
		self._settings = settings

	def get_required_property(self, name: str) -> str:
		result = self.get_optional_property(name)
		if result is None:
			raise NameError('Required property ' + name + ' was not found')
		return result

	def get_optional_property(self, name: str) -> str:
		return self._settings.get(name)
