# -*- coding: utf-8 -*-

class ServerType(object):
	"""
	A type of server available in a datacenter. Contains hardware information.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the server type. It is automatically generated and cannot be
	edited.
	"""
	server_type_id = None;

	"""
	Full bandwidth available.
	"""
	server_network_total_capacity_mbps = None;

	"""
	The name of the server type. It does not contain whitespaces. It normally
	never changes.
	"""
	server_type_name = None;

	"""
	An comprehensive server type name, which may change at any time.
	"""
	server_type_display_name = None;

	"""
	Deprecated, ignored and unused.
	"""
	server_type_label = None;

	"""
	The cores of a CPU.
	"""
	server_processor_core_count = 1;

	"""
	The clock speed of a CPU.
	"""
	server_processor_core_mhz = 1000;

	"""
	The CPU count on the server.
	"""
	server_processor_count = 1;

	"""
	The RAM capacity.
	"""
	server_ram_gbytes = 1;

	"""
	The minimum number of physical disks.
	"""
	server_disk_count = 0;

	"""
	The minimum size of a single disk.
	"""
	server_disk_size_mbytes = 0;

	"""
	The type of physical disks.
	"""
	server_disk_type = "none";

	"""
	The names of the server processors.
	"""
	server_processor_names_json = None;

	"""
	The name of the processor.
	"""
	server_processor_name = None;

	"""
	Server type very general workload type.
	"""
	server_class = "unknown";

	"""
	Specifies if the server_type is experimental and only developers have access
	to servers of this type.
	"""
	server_type_is_experimental = False;

	"""
	Number of servers provisioned. Used only for
	<code>infrastructure_deploy()</code>.
	"""
	server_count = None;

	"""
	The minimum number of GPUs.
	"""
	server_gpu_count = 0;

	"""
	The vendors of the server GPUs.
	"""
	server_gpu_vendors_json = None;

	"""
	The models of the server GPUs.
	"""
	server_gpu_models_json = None;

	"""
	The boot modes supported by servers of this type.
	"""
	server_type_boot_type = "legacy_only";

	"""
	List of tags representative for the ServerType.
	"""
	server_type_tags = [];

	"""
	The schema type
	"""
	type = None;
