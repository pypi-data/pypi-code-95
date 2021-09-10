# -*- coding: utf-8 -*-

class DriveOperation(object):
	"""
	DriveOperation contains information regarding the changes that are to be
	made to a product. Edit and deploy functions have to be called in order to
	apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, drive_label, drive_size_mbytes, drive_change_id):
		self.drive_label = drive_label;
		self.drive_size_mbytes = drive_size_mbytes;
		self.drive_change_id = drive_change_id;


	"""
	The status of the deploy process.
	"""
	drive_deploy_status = None;

	"""
	The operation applied to the Drive.
	"""
	drive_deploy_type = None;

	"""
	The Drive's label which is unique and it is used to form the
	<code>drive_subdomain</code>. It is editable and can be used to call API
	functions.
	"""
	drive_label = None;

	"""
	The Drive's fully qualified subdomain name that specifies its location in
	the infrastructure. It is a unique reference to the Drive object.
	"""
	drive_subdomain = None;

	"""
	The ID of the Drive array.
	"""
	drive_array_id = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Drive was created.
	Example format: 2013-11-29T13:00:01Z.
	"""
	drive_created_timestamp = None;

	"""
	The ID of the Drive which can be used instead of the
	<code>drive_label</code> or <code>drive_subdomain</code> when calling the
	API functions. It is automatically generated and cannot be edited.
	"""
	drive_id = None;

	"""
	The size of the Drive.
	"""
	drive_size_mbytes = None;

	"""
	The storage type of the Drive.
	"""
	drive_storage_type = None;

	"""
	The ID of the Drive's associated instance.
	"""
	instance_id = None;

	"""
	The ID of the Drive's associated container.
	"""
	container_id = None;

	"""
	Represents the volume template.
	"""
	template_id_origin = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Drive was edited.
	Example format: 2013-11-29T13:00:01Z.
	"""
	drive_updated_timestamp = None;

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
	Drive file system information
	"""
	drive_filesystem = None;
