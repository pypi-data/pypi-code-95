# -*- coding: utf-8 -*-

class AppKafka(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppKafkaInstance</a:schema> objects as values.
	"""

	def __init__(self, kafka_brokers):
		self.kafka_brokers = kafka_brokers;


	"""
	The <a:schema>AppKafkaInstance</a:schema> object which represents the
	Master.
	"""
	kafka_brokers = [];

	"""
	The connection strings to the Kafka brokers.
	"""
	kafka_brokers_connection_strings = [];

	"""
	The URL to access Kafka Manager.
	"""
	kafka_manager_url = None;

	"""
	Cluster software available versions.
	"""
	container_cluster_software_available_versions = [];

	"""
	The software version detected on the container cluster.
	"""
	container_cluster_software_version = None;

	"""
	Array of compatible and connectable clusters.
	"""
	connectable_container_clusters = [];

	"""
	The schema type
	"""
	type = None;
