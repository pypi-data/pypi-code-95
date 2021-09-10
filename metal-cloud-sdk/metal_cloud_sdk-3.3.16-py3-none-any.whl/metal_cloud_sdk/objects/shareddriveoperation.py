# -*- coding: utf-8 -*-

class SharedDriveOperation(object):
	"""
	SharedDriveOperation contains information regarding the changes that are to
	be made to a product. Edit and deploy functions have to be called in order
	to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, shared_drive_label, shared_drive_size_mbytes, shared_drive_change_id):
		self.shared_drive_label = shared_drive_label;
		self.shared_drive_size_mbytes = shared_drive_size_mbytes;
		self.shared_drive_change_id = shared_drive_change_id;


	"""
	The status of the deploy process.
	"""
	shared_drive_deploy_status = None;

	"""
	The operation applied to the SharedDrive.
	"""
	shared_drive_deploy_type = None;

	"""
	The SharedDrive's label which is unique and it is used to form the
	<code>shared_drive_subdomain</code>. It is editable and can be used to call
	API functions.
	"""
	shared_drive_label = None;

	"""
	The SharedDrive's fully qualified subdomain name that specifies its location
	in the infrastructure. It is a unique reference to the SharedDrive object.
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
	The size of the SharedDrive.
	"""
	shared_drive_size_mbytes = None;

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
	ISO 8601 timestamp which holds the date and time when the SharedDrive was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	shared_drive_updated_timestamp = None;

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

	"""
	Reserved for GUI users.
	"""
	shared_drive_gui_settings_json = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	shared_drive_change_id = None;
