# -*- coding: utf-8 -*-

class Instance(object):
	"""
	An instance represents a single server and it allows performing certain
	operations on the server which do not make sense at InstanceArray level or
	are a better fit for individual management, for example rebooting a single
	instance to not have to reboot an entire farm at the same time (to minimize
	or eliminate downtime).
	"""

	def __init__(self):
		pass;


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
	Automatically created based on <code>instance_id</code>. It is a unique
	reference to the Instance object.
	"""
	instance_subdomain_permanent = None;

	"""
	The ID of the instance which can be used instead of the
	<code>instance_label</code> or <code>instance_subdomain</code> when calling
	the API functions.  It is automatically generated and cannot be edited.
	"""
	instance_id = None;

	"""
	The ID of the InstanceArray.
	"""
	instance_array_id = None;

	"""
	The ID of the associated server.
	"""
	server_id = None;

	"""
	The instance's server_type_id.
	"""
	server_type_id = None;

	"""
	The status of the instance.
	"""
	instance_service_status = None;

	"""
	Credentials used to connect to the server through IPMI, iLO, SSH etc.
	"""
	instance_credentials = None;

	"""
	The operation type, operation status and modified instance object.
	"""
	instance_operation = None;

	"""
	An array of <a:schema>InstanceInterface</a:schema> objects indexed from 0 to
	3.
	"""
	instance_interfaces = [];

	"""
	ISO 8601 timestamp which holds the date and time when the instance was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the instance was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_updated_timestamp = "0000-00-00T00:00:00Z";

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
	List of tags representative for the Instance.
	"""
	instance_tags = [];

	"""
	Object containing custom variables and variable overrides.
	"""
	instance_custom_variables = {};
