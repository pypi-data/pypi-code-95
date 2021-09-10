# -*- coding: utf-8 -*-

class ContainerArray(object):
	"""
	A ContainerArray is a group of containers which share the same workload
	(thus enabling scalability).
	"""

	def __init__(self):
		pass;


	"""
	The ID of the ContainerArray which can be used instead of the
	<code>container_array_label</code> or <code>container_array_subdomain</code>
	when calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	container_array_id = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	container_array_change_id = None;

	"""
	The ContainerArray is a child of a ContainerCluster.
	"""
	container_cluster_id = None;

	"""
	Represents the infrastructure ID to which the ContainerArray belongs.
	"""
	infrastructure_id = None;

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
	Automatically created based on <code>container_array_id</code>. It is a
	unique reference to the ContainerArray object to be used within the
	ContainerPlatform network.
	"""
	container_array_subdomain_internal = None;

	"""
	Automatically created based on <code>container_array_id</code>. It is a
	unique reference to the load balancer of the ContainerArray object to be
	used within the ContainerPlatform network.
	"""
	container_array_load_balancer_subdomain_internal = None;

	"""
	The status of the ContainerArray.
	"""
	container_array_service_status = None;

	"""
	"""
	container_cluster_role_group = "none";

	"""
	The operation type, operation status and modified ContainerArray object.
	"""
	container_array_operation = None;

	"""
	All <a:schema>ContainerArrayInterface</a:schema> objects.
	"""
	container_array_interfaces = [];

	"""
	The resource requirements in terms of RAM for a Container of the
	ContainerArray.
	"""
	container_array_ram_mbytes = 1024;

	"""
	The resource requirements in terms of CPU cores for a Container of the
	ContainerArray.
	"""
	container_array_processor_core_count = 1;

	"""
	The number of Containers of the ContainerArray.
	"""
	container_array_container_count = 1;

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
	The <a:schema>ContainerArrayPortMapping</a:schema> objects of the
	ContainerArray.
	"""
	container_array_port_mappings = [];

	"""
	<a:schema>ContainerArrayConfigMap</a:schema> object.
	"""
	container_array_config_map = None;

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
	container_array_gui_settings_json = "";

	"""
	ISO 8601 timestamp which holds the date and time when the ContainerArray was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	container_array_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the ContainerArray was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	container_array_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The schema type.
	"""
	type = None;
