# -*- coding: utf-8 -*-

class AppPostgreSQL(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppPostgreSQL</a:schema> objects as values.
	"""

	def __init__(self, postgresql_node):
		self.postgresql_node = postgresql_node;


	"""
	The <a:schema>AppPostgreSQLInstance</a:schema> object which represents the
	Master.
	"""
	postgresql_node = [];

	"""
	The connection strings to the PostgreSQL app.
	"""
	postgresql_connection_strings = [];

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
	The default username.
	"""
	postgresql_username = None;

	"""
	The default password.
	"""
	postgresql_password = None;

	"""
	The name of the database.
	"""
	postgresql_database = None;

	"""
	The schema type
	"""
	type = None;
