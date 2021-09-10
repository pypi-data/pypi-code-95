# -*- coding: utf-8 -*-

class ContainerArrayPersistentVolume(object):
	"""
	ContainerArray persistent storage resource.
	"""

	def __init__(self, persistent_volume_name, persistent_volume_type, persistent_volume_mount_path):
		self.persistent_volume_name = persistent_volume_name;
		self.persistent_volume_type = persistent_volume_type;
		self.persistent_volume_mount_path = persistent_volume_mount_path;


	"""
	Persistent volume name.
	"""
	persistent_volume_name = None;

	"""
	Persistent volume type.
	"""
	persistent_volume_type = None;

	"""
	Persistent volume container mount path.
	"""
	persistent_volume_mount_path = None;

	"""
	The schema type.
	"""
	type = None;
