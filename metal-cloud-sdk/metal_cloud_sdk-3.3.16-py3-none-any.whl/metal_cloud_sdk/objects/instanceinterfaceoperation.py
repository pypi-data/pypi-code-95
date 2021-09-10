# -*- coding: utf-8 -*-

class InstanceInterfaceOperation(object):
	"""
	InstanceInterfaceOperation contains information regarding the changes that
	are to be made to a product. Edit and deploy functions have to be called in
	order to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, instance_interface_change_id):
		self.instance_interface_change_id = instance_interface_change_id;


	"""
	The instance_interface's label which is unique and it is used to form the
	<code>instance_interface_subdomain</code>. Can be used to call API
	functions.
	"""
	instance_interface_label = None;

	"""
	Automatically created based on <code>instance_interface_label</code>. It is
	a unique reference to the InstanceInterface object.
	"""
	instance_interface_subdomain = None;

	"""
	The status of the deploy process.
	"""
	instance_interface_deploy_status = None;

	"""
	The operation applied to instance interface.
	"""
	instance_interface_deploy_type = None;

	"""
	The ID of the instance interface.
	"""
	instance_interface_id = None;

	"""
	The ID of the instance to which the interface belongs.
	"""
	instance_id = None;

	"""
	The ID of the network to which the instance's interface is connected.
	"""
	network_id = None;

	"""
	Array of interface indexes which are part of a link aggregation together
	with this interface. The current interface is never included in this array,
	even if part of a link aggregation.
	"""
	instance_interface_lagg_indexes = [];

	"""
	Shows the index of the interface. Numbering starts at 0.
	"""
	instance_interface_index = None;

	"""
	Shows the capacity of the instance.
	"""
	instance_interface_capacity_mbps = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	This value helps check against edit requests on expired objects.
	"""
	instance_interface_change_id = None;
