# -*- coding: utf-8 -*-

class ContainerOperation(object):
	"""
	A Container is a child product of the ContainerArray and represents a
	compute node.
	"""

	def __init__(self, container_label):
		self.container_label = container_label;


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
	The operation applied to the Container.
	"""
	container_deploy_type = None;

	"""
	The status of the deploy process.
	"""
	container_deploy_status = None;

	"""
	All <a:schema>ContainerInterfaceOperation</a:schema> objects.
	"""
	container_interfaces = [];

	"""
	ISO 8601 timestamp which holds the date and time when the Container was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	container_updated_timestamp = None;

	"""
	The schema type.
	"""
	type = None;
