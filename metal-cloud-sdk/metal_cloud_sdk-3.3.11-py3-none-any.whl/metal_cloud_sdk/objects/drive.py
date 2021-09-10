# -*- coding: utf-8 -*-

class Drive(object):
	"""
	A Drive is a storage device mounted via iSCSI.
	"""

	def __init__(self, drive_size_mbytes):
		self.drive_size_mbytes = drive_size_mbytes;


	"""
	The Drive's label which is unique and it is used to form the
	<code>drive_subdomain</code>. It is editable and can be used to call API
	functions.
	"""
	drive_label = None;

	"""
	Automatically created based on <code>drive_label</code>. It is a unique
	reference to the Drive object.
	"""
	drive_subdomain = None;

	"""
	The ID of the Drive which can be used instead of the
	<code>drive_label</code> or <code>drive_subdomain</code> when calling the
	API functions. It is automatically generated and cannot be edited.
	"""
	drive_id = None;

	"""
	The ID of the Drive array.
	"""
	drive_array_id = None;

	"""
	Represents the associated instance's ID.
	"""
	instance_id = None;

	"""
	Represents the associated container's ID.
	"""
	container_id = None;

	"""
	Represents the capacity of the Drive.
	"""
	drive_size_mbytes = None;

	"""
	Represents the Drive’s type of storage.
	"""
	drive_storage_type = "iscsi_ssd";

	"""
	Represents the infrastructure ID to which the Drive belongs.
	"""
	infrastructure_id = None;

	"""
	Represents the volume template.
	"""
	template_id_origin = None;

	"""
	Information to connect via iSCSI or bootable drive associated credentials.
	"""
	drive_credentials = None;

	"""
	It shows the status of the Drive.
	"""
	drive_service_status = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Drive was created.
	Example format: 2013-11-29T13:00:01Z.
	"""
	drive_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the Drive was edited.
	Example format: 2013-11-29T13:00:01Z.
	"""
	drive_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The operation type, operation status and modified Drive object.
	"""
	drive_operation = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	drive_change_id = None;

	"""
	OperatingSystem
	"""
	drive_operating_system = None;

	"""
	Ignored if the <code>drive_service_status</code> property is
	<code>SERVICE_STATUS_ACTIVE</code>
	"""
	drive_filesystem = None;
