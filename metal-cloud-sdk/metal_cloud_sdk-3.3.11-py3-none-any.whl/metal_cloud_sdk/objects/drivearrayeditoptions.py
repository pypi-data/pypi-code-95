# -*- coding: utf-8 -*-

class DriveArrayEditOptions(object):
	"""
	Available properties for the drive_array_edit function.
	"""

	def __init__(self, update_active_drives_size):
		self.update_active_drives_size = update_active_drives_size;


	"""
	If true, active Drives will be resized to the new
	<code>drive_size_mbytes_default</code> property of the parent
	<a:schema>DriveArray</a:schema>.
	"""
	update_active_drives_size = None;

	"""
	The schema type.
	"""
	type = None;
