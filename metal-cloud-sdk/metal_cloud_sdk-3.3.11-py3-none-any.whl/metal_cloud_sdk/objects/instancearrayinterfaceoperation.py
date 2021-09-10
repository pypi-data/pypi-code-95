# -*- coding: utf-8 -*-

class InstanceArrayInterfaceOperation(object):
	"""
	InstanceArrayInterfaceOperation contains information regarding the changes
	that are to be made to a product. Edit and deploy functions have to be
	called in order to apply the changes. The operation type and status are
	unique to each operation object.
	"""

	def __init__(self, instance_array_interface_id, network_id, instance_array_interface_change_id):
		self.instance_array_interface_id = instance_array_interface_id;
		self.network_id = network_id;
		self.instance_array_interface_change_id = instance_array_interface_change_id;


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
	The status of the deploy process.
	"""
	instance_array_interface_deploy_status = None;

	"""
	The operation applied to InstanceArray interface.
	"""
	instance_array_interface_deploy_type = None;

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
	ISO 8601 timestamp which holds the date and time when the InstanceArray
	interface was edited. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_array_interface_updated_timestamp = None;

	"""
	Shows the index of the interface. Numbering starts at 0.
	"""
	instance_array_interface_index = None;

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
