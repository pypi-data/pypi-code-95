# -*- coding: utf-8 -*-

class Container(object):
	"""
	A Container is a child product of the ContainerArray and represents a
	compute node.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the Container which can be used instead of the
	<code>container_label</code> or <code>container_subdomain</code> when
	calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	container_id = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	container_change_id = None;

	"""
	The Container is a child of a ContainerArray.
	"""
	container_array_id = None;

	"""
	Represents the infrastructure ID to which the Container belongs.
	"""
	infrastructure_id = None;

	"""
	The Container's unique label is used to create the
	<code>container_subdomain</code>. It is editable and can be used to call API
	functions.
	"""
	container_label = None;

	"""
	Automatically created based on <code>container_label</code>. It is a unique
	reference to the Container object.
	"""
	container_subdomain = None;

	"""
	Automatically created based on <code>container_label</code>. It is a unique
	reference to the Container object to be used within the ContainerPlatform
	network.
	"""
	container_subdomain_internal = None;

	"""
	The status of the Container.
	"""
	container_service_status = None;

	"""
	The operation type, operation status and modified Container object.
	"""
	container_operation = None;

	"""
	Credentials used to connect to the Container.
	"""
	container_credentials = None;

	"""
	All <a:schema>ContainerInterface</a:schema> objects.
	"""
	container_interfaces = [];

	"""
	The index of the Container within the ContainerArray.
	"""
	container_index = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Container was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	container_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the Container was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	container_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The schema type.
	"""
	type = None;
