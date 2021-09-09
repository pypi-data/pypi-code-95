import json
import random
import uuid
from datetime import datetime
from typing import Dict
import pytz
from paho.mqtt.client import MQTTv311
import paho.mqtt.client as mqtt  # Keep this for the test suite to work


from .mqtt_operation_cache import OperationQueue, Operation, OperationType
from ...config.mqtt_topics_config import MQTTTopicsConfig
from ...enums.job_status import JobStatus
from ...enums.sensor_type import SensorType
from ...handlers.mqtt import *
from ...pyzio_listener import PyzioListener
from ...pyzio_logger import PyzioLogger
from ...service.job_service import JobService
from ...service.printer_service import PrinterService
from ...exceptions.variable_exceptions import UnassignedVariable
from ...exceptions import error_messages


class PhasioMQTTAdapter(PhasioMQTTPort):

	def __init__(self,
				 logger: PyzioLogger,
				 job_service: JobService,
				 update_service: UpdateService,
				 mqtt_config: MQTTTopicsConfig,
				 printer_service: PrinterService,
				 listener: PyzioListener):
		self._mqtt_config = mqtt_config
		self._client = None
		self._logger = logger
		self._job_service = job_service
		self._update_service = update_service
		self._printer_service = printer_service
		self._listener = listener
		self._message_handlers = self._build_message_handlers()
		self._message_queue = OperationQueue()

	def candidate_connect(self) -> None:
		import paho.mqtt.client as mqtt
		username = f'candidate-{self._printer_service.get_candidate_id()}'
		self._client = mqtt.Client(client_id=username, clean_session=False, protocol=MQTTv311)
		password = self._printer_service.get_secret()
		self._client.tls_set()
		self._client.username_pw_set(username, password)
		self._assign_mqtt_events()
		self._client.connect_async(self._mqtt_config.host(), self._mqtt_config.port())
		self._client.loop_start()

	def printer_connect(self) -> None:
		import paho.mqtt.client as mqtt
		username = str(self._printer_service.get_printer_id())
		self._client = mqtt.Client(client_id=username, clean_session=False, protocol=MQTTv311)
		password = self._printer_service.get_secret()
		self._client.tls_set()
		self._client.username_pw_set(username, password)
		self._assign_mqtt_events()
		self._client.connect_async(self._mqtt_config.host(), self._mqtt_config.port())
		self._client.loop_start()

	def disconnect(self) -> None:
		self._client.loop_stop()
		self._client.disconnect()

	def shutdown(self) -> None:
		self._unsubscribe_from_topic(self._topic_for_getting_job_commands())
		self._client.loop_stop()
		self.disconnect()

	def set_printer_id(self, printer_id: str) -> None:
		self._printer_service.get_printer_id()

	def get_printer_id(self) -> str:
		return self._printer_service.get_printer_id()

	def register_sensor(self, sensor_name: str, sensor_type: SensorType) -> str:
		msg, request_id = self._create_sensor_registration_message(sensor_name, sensor_type)
		msg_string = json.dumps(msg)
		self._mqtt_publish(self._topic_for_sending_sensor_registration(), msg_string)
		return request_id

	def stream_sensor_data(self, sensor_id: str, value: float) -> None:
		msg = self._create_reading_message(sensor_id, value)
		msg_string = json.dumps(msg)
		self._mqtt_publish(self._topic_for_sending_sensor_readings(), msg_string)

	def send_job_updates(self, job_id: str, status: JobStatus) -> None:
		msg = self._create_job_update_message(job_id, status)
		msg_string = json.dumps(msg)
		self._mqtt_publish(self._topic_for_sending_job_updates(), msg_string)

	def finish_registration(self, printer_id: str) -> None:
		self._unsubscribe_from_topic(self._topic_for_getting_printer_id())
		self.disconnect()
		self.printer_connect()

	def listen_for_printer_id(self) -> None:
		topic_name = self._topic_for_getting_printer_id()
		self._subscribe_to_topic(topic_name)

	def listen_for_sensor_ids(self) -> None:
		topic_name = self._topic_for_getting_sensor_ids()
		self._subscribe_to_topic(topic_name)

	def begin_listening(self) -> None:
		topic_name = self._topic_for_getting_job_commands()
		self._subscribe_to_topic(topic_name)

	def _assign_mqtt_events(self):
		self._client.on_connect = self._on_connect
		self._client.on_message = self._on_message
		self._client.on_subscribe = self._on_subscribe
		self._client.on_disconnect = self._on_disconnect

	def _mqtt_publish(self, topic: str, message: str, qos: int = 1, retain: bool = False):
		if not self._client.is_connected():
			self._logger.info("Queuing pub on topic " + str(topic) + ":  " + str(message))
			operation = Operation(OperationType.PUB, topic=topic, message=message, qos=qos, retain=retain)
			self._message_queue.push(operation)
			return
		self._logger.info("Publishing message on topic " + str(topic) + ": " + str(message))
		self._client.publish(topic, payload=message, qos=qos, retain=retain)

	def _on_subscribe(self, client, userdata, mid, granted_qos) -> None:
		self._logger.info("Subscribed")

	def _on_connect(self, client, userdata, flags, rc) -> None:
		self._execute_queued_operations()
		if not rc == 0:
			self._logger.info("Connection to mqtt broker refused, code " + str(rc))
		else:
			self._logger.info("Connected with result  code " + str(rc))

	def _execute_queued_operations(self):
		self._logger.info("Executing queued operations")
		while not self._message_queue.isempty():
			op = self._message_queue.pop()
			if op.type == OperationType.PUB:
				self._mqtt_publish(op.topic, op.message, op.qos, op.retain)
			elif op.type == OperationType.SUB:
				self._subscribe_to_topic(op.topic)

	def _on_disconnect(self, client, userdata, rc):
		if not rc == 0:
			self._logger.info("Disconnected from mqtt broker for unknown reasons (network error?), rc = {}".format(rc))
		else:
			self._logger.info("Disconnected from mqtt broker")

	def _on_message(self, client, userdata, msg) -> None:
		self._logger.info("Received message on topic " + str(msg.topic) + ": " + str(msg.payload))
		payload = json.loads(msg.payload)
		message_type = payload['type']
		handler = self._message_handlers[message_type]
		handler.handle(payload)

	def _topic_for_getting_printer_id(self) -> str:
		base_topic = self._mqtt_config.printer_registration_ack_topic()
		candidate_id = self._printer_service.get_candidate_id()

		if candidate_id is not None:
			return f'{base_topic}/{candidate_id}'
		else:
			raise UnassignedVariable(error_messages.no_candidate_for_printer_ack)

	def _topic_for_getting_sensor_ids(self) -> str:
		base_topic = self._mqtt_config.sensor_registration_ack_topic()
		printer_id = self._printer_service.get_printer_id()

		if printer_id is not None:
			return f'{base_topic}/{printer_id}'
		else:
			raise UnassignedVariable(error_messages.no_printer_for_sensor_ack)

	def _topic_for_sending_sensor_registration(self) -> str:
		base_topic = self._mqtt_config.sensor_registration_topic()
		printer_id = self._printer_service.get_printer_id()

		if printer_id is not None:
			return f'{base_topic}/{printer_id}'
		else:
			raise UnassignedVariable(error_messages.no_printer_for_sensor_reg)

	def _topic_for_sending_sensor_readings(self) -> str:
		base_topic = self._mqtt_config.sensor_readings_topic()
		printer_id = self._printer_service.get_printer_id()

		if printer_id is not None:
			return f'{base_topic}/{printer_id}'
		else:
			raise UnassignedVariable(error_messages.no_printer_for_sensor_readings)

	def _topic_for_sending_job_updates(self) -> str:
		base_topic = self._mqtt_config.job_updates_topic()
		printer_id = self._printer_service.get_printer_id()

		if printer_id is not None:
			return f'{base_topic}/{printer_id}'
		else:
			raise UnassignedVariable(error_messages.no_printer_for_job_updates)

	def _topic_for_getting_job_commands(self) -> str:
		base_topic = self._mqtt_config.command_topic()
		printer_id = self._printer_service.get_printer_id()

		if printer_id is not None:
			return f'{base_topic}/{printer_id}'
		else:
			raise UnassignedVariable(error_messages.no_printer_for_job_commands)

	def _subscribe_to_topic(self, topic: str) -> None:
		if not self._client.is_connected():
			self._logger.info("Queuing sub" + topic)
			operation = Operation(OperationType.SUB, topic=topic)
			self._message_queue.push(operation)
			return
		self._logger.info("Subscribing " + topic)
		self._client.subscribe(topic, qos=0)

	def _unsubscribe_from_topic(self, topic: str) -> None:
		self._logger.info("Unsubscribing" + topic)
		self._client.unsubscribe(topic)

	def _build_message_handlers(self) -> Dict[str, MessageHandler]:
		handlers = dict()
		for handler_class in MessageHandler.__subclasses__():
			handler = handler_class(self._logger, self._job_service, self._update_service, self._printer_service, self, self._listener)
			handlers[handler.can_handle().name] = handler
		return handlers

	def _create_printer_registration_message(self, brand: str, model: str, material: str):
		r_id = self._generate_uuid()
		pairing_code = random.randint(999, 99999)
		reading = {
			'brand': brand,
			'requestId': r_id,
			'model': model,
			'material': material,
			'pairingCode': pairing_code,
			'measurementTime': self._get_date()
		}
		self._logger.info("Pairing code is " + str(pairing_code))
		return reading, r_id, str(pairing_code)

	def _create_sensor_registration_message(self, sensor_name: str, sensor_type: SensorType):
		r_id = self._generate_uuid()
		reading = {
			'requestId': r_id,
			'printerId': self.get_printer_id(),
			'sensorName': sensor_name,
			'sensorType': sensor_type,
			'measurementTime': self._get_date()
		}
		return reading, r_id

	def _create_reading_message(self, sensor_id: str, value: float):
		reading = {
			'requestId': self._generate_uuid(),
			'sensorId': sensor_id,
			'value': value,
			'measurementTime': self._get_date()
		}
		return reading

	def _create_job_update_message(self, job_id: str, status: JobStatus):
		job_update = {
			'jobId': job_id,
			'requestId': self._generate_uuid(),
			'printerId': self.get_printer_id(),
			'status': status,
			'measurementTime': self._get_date()
		}
		return job_update

	def _get_date(self) -> str:
		return pytz.utc.localize(datetime.utcnow()).isoformat()

	def _generate_uuid(self) -> str:
		return str(uuid.uuid4())
