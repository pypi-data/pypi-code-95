# -*- coding: utf-8 -*-

class Network(object):
	"""
	A Network object contains information regarding a network, including type,
	parent <a:schema>Infrastructure</a:schema> and creation time.
	"""

	def __init__(self, network_type):
		self.network_type = network_type;


	"""
	The network's label which is unique and it is used to form the
	<code>network_subdomain</code>. Can be used to call API functions.
	"""
	network_label = None;

	"""
	Automatically created based on <code>network_label</code>. It is a unique
	reference to the Network object.
	"""
	network_subdomain = None;

	"""
	Represents the ID of the network which can be used instead of the
	<code>network_label</code> or <code>network_subdomain</code> when calling
	the API functions.  It is automatically generated and cannot be edited.
	"""
	network_id = None;

	"""
	The network type.
	"""
	network_type = None;

	"""
	Represents the infrastructure ID to which the network belongs.
	"""
	infrastructure_id = None;

	"""
	It shows the status of the network.
	"""
	network_service_status = None;

	"""
	The operation type, operation status and modified Network object.
	"""
	network_operation = None;

	"""
	ISO 8601 timestamp which holds the date and time when the network was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	network_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the network was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	network_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	Reserved for GUI users.
	"""
	network_gui_settings_json = "";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	network_change_id = None;

	"""
	The VLAN ID allocated for this network.
	"""
	network_vlan_id = None;

	"""
	The network suspend status.
	"""
	network_suspend_status = None;

	"""
	This property specify whether the allocation of the private IPS is done
	automatically or manually.
	"""
	network_lan_autoallocate_ips = False;
