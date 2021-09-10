# -*- coding: utf-8 -*-

class ContainerArrayVolatileVolume(object):
	"""
	ContainerArray volatile storage resource.
	"""

	def __init__(self, volatile_volume_name, volatile_volume_type, volatile_volume_mount_path):
		self.volatile_volume_name = volatile_volume_name;
		self.volatile_volume_type = volatile_volume_type;
		self.volatile_volume_mount_path = volatile_volume_mount_path;


	"""
	Volatile volume name.
	"""
	volatile_volume_name = None;

	"""
	Volatile volume type.
	"""
	volatile_volume_type = None;

	"""
	Volatile volume container mount path.
	"""
	volatile_volume_mount_path = None;

	"""
	The schema type.
	"""
	type = None;
