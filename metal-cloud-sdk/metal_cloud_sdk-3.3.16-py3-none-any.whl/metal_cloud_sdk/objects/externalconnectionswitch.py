# -*- coding: utf-8 -*-

class ExternalConnectionSwitch(object):
	"""
	An external connection switch object holds a reference to a network
	equipment (switch) and a list of allowed ports.
	"""

	def __init__(self, network_equipment_id):
		self.network_equipment_id = network_equipment_id;


	"""
	List of port label used on the referenced network equipment.
	"""
	external_connection_switch_ports = [];

	"""
	The ID of the external connection switch entry.
	"""
	external_connection_switch_id = None;

	"""
	The ID of the external connection to which the switch entry is attached.
	"""
	external_connection_id = None;

	"""
	The ID of the network equipment (switch) referenced by this switch entry.
	"""
	network_equipment_id = None;

	"""
	The schema type.
	"""
	type = None;
