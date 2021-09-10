# -*- coding: utf-8 -*-

class InstanceOperation(object):
	"""
	InstanceOperation contains information regarding the changes that are to be
	made to a product. Edit and deploy functions have to be called in order to
	apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, instance_label, server_type_id, instance_change_id):
		self.instance_label = instance_label;
		self.server_type_id = server_type_id;
		self.instance_change_id = instance_change_id;


	"""
	The operation applied to the instance.
	"""
	instance_deploy_type = None;

	"""
	The status of the deploy process.
	"""
	instance_deploy_status = None;

	"""
	The instance's label which is unique and it is used to form the
	<code>instance_subdomain</code>. Can be used to call API functions.
	"""
	instance_label = None;

	"""
	Automatically created based on <code>instance_label</code>. It is a unique
	reference to the Instance object.
	"""
	instance_subdomain = None;

	"""
	The ID of the instance which can be used instead of the
	<code>instance_label</code> or <code>instance_subdomain</code> when calling
	the API functions.
	"""
	instance_id = None;

	"""
	The ID of the InstanceArray.
	"""
	instance_array_id = None;

	"""
	ISO 8601 timestamp which holds the date and time when the instance was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_updated_timestamp = None;

	"""
	The ID of the associated server.
	"""
	server_id = None;

	"""
	The instance's server_type_id.
	"""
	server_type_id = None;

	"""
	The ID of the drive the instance boots from.
	"""
	drive_id_bootable = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	instance_change_id = None;

	"""
	Represents the volume template.
	"""
	template_id_origin = None;

	"""
	Object containing custom variables and variable overrides.
	"""
	instance_custom_variables = {};
