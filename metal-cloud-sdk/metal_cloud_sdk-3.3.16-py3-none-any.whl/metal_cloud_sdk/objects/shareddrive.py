# -*- coding: utf-8 -*-

class SharedDrive(object):
	"""
	A SharedDrive is a storage device mounted via iSCSI that is accessible to
	multiple instance arrays.
	"""

	def __init__(self, shared_drive_attached_instance_arrays, shared_drive_attached_container_arrays):
		self.shared_drive_attached_instance_arrays = shared_drive_attached_instance_arrays;
		self.shared_drive_attached_container_arrays = shared_drive_attached_container_arrays;


	"""
	The SharedDrive's label which is unique and it is used to form the
	<code>shared_drive_subdomain</code>. It is editable and can be used to call
	API functions.
	"""
	shared_drive_label = None;

	"""
	Automatically created based on <code>shared_drive_label</code>. It is a
	unique reference to the SharedDrive object.
	"""
	shared_drive_subdomain = None;

	"""
	The ID of the SharedDrive which can be used instead of the
	<code>shared_drive_label</code> or <code>shared_drive_subdomain</code> when
	calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	shared_drive_id = None;

	"""
	Represents the capacity of the SharedDrive.
	"""
	shared_drive_size_mbytes = 2048;

	"""
	The storage type of the SharedDrive.
	"""
	shared_drive_storage_type = None;

	"""
	This feature is no longer available. The flag is ignored. Indicates if the
	instances attached to this SharedDrive will have GFS installed and that they
	will mount this SharedDrive (only supported for Centos 7.x).
	"""
	shared_drive_has_gfs = False;

	"""
	Represents the infrastructure ID to which the SharedDrive belongs.
	"""
	infrastructure_id = None;

	"""
	It shows the status of the SharedDrive.
	"""
	shared_drive_service_status = None;

	"""
	ISO 8601 timestamp which holds the date and time when the SharedDrive was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	shared_drive_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the SharedDrive was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	shared_drive_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The operation type, operation status and modified SharedDrive object.
	"""
	shared_drive_operation = None;

	"""
	Reserved for GUI users.
	"""
	shared_drive_gui_settings_json = "";

	"""
	"""
	shared_drive_credentials = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	shared_drive_change_id = None;

	"""
	Contains the attached InstanceArray IDs.
	"""
	shared_drive_attached_instance_arrays = [];

	"""
	Contains the attached ContainerArray IDs.
	"""
	shared_drive_attached_container_arrays = [];

	"""
	The schema type.
	"""
	type = None;
