# -*- coding: utf-8 -*-

class DriveArrayFilesystem(object):
	"""
	Contains details about the file system of the Drives belonging to a
	DriveArray.
	"""

	def __init__(self, drive_array_filesystem_type_default, drive_array_filesystem_block_size_bytes_default):
		self.drive_array_filesystem_type_default = drive_array_filesystem_type_default;
		self.drive_array_filesystem_block_size_bytes_default = drive_array_filesystem_block_size_bytes_default;


	"""
	The file system type of the Drives belonging to a DriveArray.
	"""
	drive_array_filesystem_type_default = None;

	"""
	The file system block size of the Drives belonging to a DriveArray.
	"""
	drive_array_filesystem_block_size_bytes_default = None;

	"""
	The schema type
	"""
	type = None;
