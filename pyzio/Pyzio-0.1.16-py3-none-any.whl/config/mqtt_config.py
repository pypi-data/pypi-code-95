from .generic_config import GenericConfig


class MQTTConfig(GenericConfig):

	def host(self) -> str:
		return self.get_required_property('mqtt.broker')

	def port(self) -> str:
		return self.get_required_property('mqtt.port')
