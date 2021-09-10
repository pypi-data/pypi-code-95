# -*- coding: utf-8 -*-

class ContainerArrayOperation(object):
	"""
	ContainerArrayOperation contains information regarding the changes that are
	to be made to a product. Edit and deploy functions have to be called in
	order to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, container_array_change_id, container_array_label, container_array_ram_mbytes, container_array_processor_core_count, container_array_container_count):
		self.container_array_change_id = container_array_change_id;
		self.container_array_label = container_array_label;
		self.container_array_ram_mbytes = container_array_ram_mbytes;
		self.container_array_processor_core_count = container_array_processor_core_count;
		self.container_array_container_count = container_array_container_count;


	"""
	The ID of the ContainerArray which can be used instead of the
	<code>container_array_label</code> or <code>container_array_subdomain</code>
	when calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	container_array_id = None;

	"""
	This property helps ensure that edit operations don't overwrite other, more
	recent changes made to the same object. It gets updated automatically after
	each successful edit operation.
	"""
	container_array_change_id = None;

	"""
	The ContainerArray's unique label is used to create the
	<code>container_array_subdomain</code>. It is editable and can be used to
	call API functions.
	"""
	container_array_label = None;

	"""
	Automatically created based on <code>container_array_label</code>. It is a
	unique reference to the ContainerArray object.
	"""
	container_array_subdomain = None;

	"""
	The operation applied to the ContainerArray.
	"""
	container_array_deploy_type = None;

	"""
	The status of the deploy process.
	"""
	container_array_deploy_status = None;

	"""
	All <a:schema>ContainerArrayInterfaceOperation</a:schema> objects.
	"""
	container_array_interfaces = [];

	"""
	The resource requirements in terms of RAM for a Container of the
	ContainerArray.
	"""
	container_array_ram_mbytes = None;

	"""
	The resource requirements in terms of CPU cores for a Container of the
	ContainerArray.
	"""
	container_array_processor_core_count = None;

	"""
	The number of Containers of the ContainerArray.
	"""
	container_array_container_count = None;

	"""
	The Docker image of the ContainerArray.
	"""
	container_array_application_image = "bigstepinc/hello-world";

	"""
	Container entrypoint command override for the ContainerArray.
	"""
	container_array_entrypoint_command_override = [];

	"""
	Container entrypoint arguments for the ContainerArray.
	"""
	container_array_entrypoint_args = [];

	"""
	The <a:schema>ContainerArrayEnvironmentVariable</a:schema> objects of the
	ContainerArray.
	"""
	container_array_environment_variables = [];

	"""
	<a:schema>ContainerArrayConfigMap</a:schema> object.
	"""
	container_array_config_map = None;

	"""
	The <a:schema>ContainerArrayPortMapping</a:schema> objects of the
	ContainerArray.
	"""
	container_array_port_mappings = [];

	"""
	The <a:schema>ContainerArraySecret</a:schema> objects of the ContainerArray.
	"""
	container_array_secrets = [];

	"""
	The <a:schema>ContainerArrayVolatileVolume</a:schema> objects of the
	ContainerArray.
	"""
	container_array_volatile_volumes = [];

	"""
	The <a:schema>ContainerArrayPersistentVolume</a:schema> objects of the
	ContainerArray.
	"""
	container_array_persistent_volumes = [];

	"""
	<a:schema>ContainerArrayReadinessCheck</a:schema> object that asseses the
	readiness of the ContainerArray Containers.
	"""
	container_array_readiness_check = None;

	"""
	<a:schema>ContainerArrayLivenessCheck</a:schema> object that asseses the
	liveness of the ContainerArray Containers.
	"""
	container_array_liveness_check = None;

	"""
	Reserved for GUI users.
	"""
	container_array_gui_settings_json = None;

	"""
	ISO 8601 timestamp which holds the date and time when the ContainerArray was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	container_array_updated_timestamp = None;

	"""
	The schema type.
	"""
	type = None;
