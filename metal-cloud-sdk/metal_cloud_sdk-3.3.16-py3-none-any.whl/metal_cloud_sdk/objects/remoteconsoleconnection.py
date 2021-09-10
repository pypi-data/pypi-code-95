# -*- coding: utf-8 -*-

class RemoteConsoleConnection(object):
	"""
	Information needed by Tomcat and Guacd services to connect to the server.
	"""

	def __init__(self, connection_user_id):
		self.connection_user_id = connection_user_id;


	"""
	The ID of the user.
	"""
	connection_user_id = None;

	"""
	Username of the server which is used for the connection.
	"""
	connection_username = None;

	"""
	Name of the host.
	"""
	connection_host = None;

	"""
	The port used to connect.
	"""
	connection_port = None;

	"""
	Private key used for the connection.
	"""
	connection_private_key = None;

	"""
	Exception if user is not authorized.
	"""
	connection_cookieAuthorizationException = None;

	"""
	The schema type
	"""
	type = None;
