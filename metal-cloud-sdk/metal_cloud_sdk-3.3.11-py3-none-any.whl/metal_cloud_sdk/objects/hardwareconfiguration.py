# -*- coding: utf-8 -*-

class HardwareConfiguration(object):
	"""
	HardwareConfiguration holds the desired hardware configuration when trying
	to find available servers for provisioning.
	"""

	def __init__(self):
		pass;


	"""
	The minimum RAM capacity of each instance.
	"""
	instance_array_ram_gbytes = 0;

	"""
	The CPU count on each instance.
	"""
	instance_array_processor_count = 0;

	"""
	The minimum clock speed of a CPU.
	"""
	instance_array_processor_core_mhz = 0;

	"""
	The minimum cores of a CPU.
	"""
	instance_array_processor_core_count = 0;

	"""
	The minumim of total MHz of the instance.
	"""
	instance_array_total_mhz = None;

	"""
	The maximum number of instances in an InstanceArray.
	"""
	instance_array_instance_count = 0;

	"""
	The minimum number of physical disks.
	"""
	instance_array_disk_count = 0;

	"""
	The minimum size of a single disk.
	"""
	instance_array_disk_size_mbytes = 0;

	"""
	The types of physical disks.
	"""
	instance_array_disk_types = None;

	"""
	The schema type
	"""
	type = None;
