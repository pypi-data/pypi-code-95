# -*- coding: utf-8 -*-

class InstanceArrayInterface(object):
	"""
	An InstanceArray interface is used to attach all the corresponding instance
	interfaces to a network.
	"""

	def __init__(self):
		pass;


	"""
	The instance_array_interface's label which is unique and it is used to form
	the <code>instance_array_interface_subdomain</code>. Can be used to call API
	functions.
	"""
	instance_array_interface_label = None;

	"""
	Automatically created based on <code>instance_array_interface_label</code>.
	It is a unique reference to the InstanceArrayInterface object.
	"""
	instance_array_interface_subdomain = None;

	"""
	The ID of the InstanceArray interface.
	"""
	instance_array_interface_id = None;

	"""
	The ID of the InstanceArray that the interface belongs to.
	"""
	instance_array_id = None;

	"""
	The ID of the network to which the InstanceArray interface is attached.
	"""
	network_id = None;

	"""
	Array of interface indexes which are part of a link aggregation together
	with this interface. The current interface is never included in this array,
	even if part of a link aggregation.
	"""
	instance_array_interface_lagg_indexes = [];

	"""
	Shows the index of the interface. Numbering starts at 0.
	"""
	instance_array_interface_index = None;

	"""
	The status of the InstanceArray interface.
	"""
	instance_array_interface_service_status = None;

	"""
	The operation type, operation status and modified InstanceArray Interface
	object.
	"""
	instance_array_interface_operation = None;

	"""
	ISO 8601 timestamp which holds the date and time when the InstanceArray
	interface was created. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_array_interface_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the InstanceArray
	interface was edited. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_array_interface_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	instance_array_interface_change_id = None;

	"""
	dns_subdomain_id
	"""
	dns_subdomain_id = None;

	"""
	dns_subdomain_permanent_id
	"""
	dns_subdomain_permanent_id = None;

	"""
	instance_array_interface_is_api_private
	"""
	instance_array_interface_is_api_private = False;

	"""
	infrastructure_id
	"""
	infrastructure_id = None;

	"""
	instance_array_interface_subdomain_permanent
	"""
	instance_array_interface_subdomain_permanent = None;

	"""
	instance_array_interface_gui_settings_json
	"""
	instance_array_interface_gui_settings_json = None;
