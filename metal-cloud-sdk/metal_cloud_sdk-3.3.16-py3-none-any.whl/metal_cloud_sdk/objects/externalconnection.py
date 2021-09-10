# -*- coding: utf-8 -*-

class ExternalConnection(object):
	"""
	An external connection can be attached to a network object.
	"""

	def __init__(self, external_connection_label):
		self.external_connection_label = external_connection_label;


	"""
	The ID of the external connection.
	"""
	external_connection_id = None;

	"""
	The label of the external connection.
	"""
	external_connection_label = None;

	"""
	The description of the external connection.
	"""
	external_connection_description = None;

	"""
	Marks an external connection as not ready to be used or deprecated.
	"""
	external_connection_hidden = False;

	"""
	The name of the <a:schema>Datacenter</a:schema>
	"""
	datacenter_name = None;

	"""
	An array of <a:schema>ExternalConnectionSwitch</a:schema> objects.
	"""
	external_connection_switches = None;

	"""
	The schema type.
	"""
	type = None;
