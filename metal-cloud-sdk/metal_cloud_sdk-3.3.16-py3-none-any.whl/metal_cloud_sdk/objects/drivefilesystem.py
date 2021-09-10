# -*- coding: utf-8 -*-

class DriveFilesystem(object):
	"""
	Contains details about the file system of a Drive.
	"""

	def __init__(self, drive_filesystem_type, drive_filesystem_block_size_bytes):
		self.drive_filesystem_type = drive_filesystem_type;
		self.drive_filesystem_block_size_bytes = drive_filesystem_block_size_bytes;


	"""
	The file system type of the Drive.
	"""
	drive_filesystem_type = None;

	"""
	The file system block size of the Drive.
	"""
	drive_filesystem_block_size_bytes = None;

	"""
	The path where the Drive is or will be mounted.
	"""
	drive_filesystem_mount_path = None;

	"""
	The schema type
	"""
	type = None;
