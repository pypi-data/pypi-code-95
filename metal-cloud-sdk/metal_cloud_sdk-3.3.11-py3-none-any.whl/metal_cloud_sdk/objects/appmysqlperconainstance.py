# -*- coding: utf-8 -*-

class AppMysqlPerconaInstance(object):
	"""
	Details about the Instance object specific to MySQLPercona. The information
	presented here is obtained by interrogating the MySQLPercona API. Backward
	compatibility object will not be ensured when the underlying MySQLPercona
	API changes.
	"""

	def __init__(self):
		pass;


	"""
	The initial admin username on the instance.
	"""
	admin_username = None;

	"""
	The initial admin password on the instance.
	"""
	admin_initial_password = None;

	"""
	The name of the instance. Usually the IP of the instance.
	"""
	hostname = None;

	"""
	The port used for the MySQL connection.
	"""
	port = None;

	"""
	The health status of the instance.
	"""
	status = None;

	"""
	The version of the MySQLPercona software.
	"""
	version = None;

	"""
	"""
	memoryTotal = None;

	"""
	"""
	memoryFree = None;

	"""
	The ID of the instance associated with the node
	"""
	instance_id = None;

	"""
	The label of the instance associated with the node
	"""
	instance_label = None;

	"""
	The schema type
	"""
	type = None;
