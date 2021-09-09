from .mqtt_config import MQTTConfig


class MQTTTopicsConfig(MQTTConfig):

	def printer_registration_topic(self) -> str:
		return "printer_registration_in"

	def printer_registration_ack_topic(self) -> str:
		return "printer_registration"

	def sensor_registration_topic(self) -> str:
		return "sensor_registration_in"

	def sensor_registration_ack_topic(self) -> str:
		return "sensor_registration_topic"

	def command_topic(self) -> str:
		return "command"

	def job_updates_topic(self) -> str:
		return "job_status_updates"

	def sensor_readings_topic(self) -> str:
		return "sensor_readings"
