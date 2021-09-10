# -*- coding: utf-8 -*-

class IndependentInstanceDriveConfig(object):
	"""
	Configuration info for a local or iSCSI drive used on an independent
	instance.
	"""

	def __init__(self, drive_mount_type):
		self.drive_mount_type = drive_mount_type;


	"""
	Determines wether the drive is local to the server or mounted via iSCSI.
	"""
	drive_mount_type = None;

	"""
	The volume template ID.
	"""
	volume_template_id = None;

	"""
	If the drive_mount_type is pxe_iscsi, represents the Drive’s type of
	storage.
	"""
	drive_storage_type = None;

	"""
	If the drive_mount_type is pxe_iscsi, represents the capacity of the Drive.
	"""
	drive_size_mbytes = None;

	"""
	The Drive's label which is unique and it is used to form the
	<code>drive_subdomain</code>. It's only used for iSCSI drives. If this is
	not given, a <code>drive-<drive_id></code> label will be used instead.
	"""
	drive_label = None;

	"""
	License utilization type for the license used on the drive.
	"""
	license_utilization_type = "subscription";

	"""
	The schema type.
	"""
	type = None;
