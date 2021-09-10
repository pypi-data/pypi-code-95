# -*- coding: utf-8 -*-

class DriveArrayOperation(object):
	"""
	DriveArrayOperation contains information regarding the changes that are to
	be made to a product. Edit and deploy functions have to be called in order
	to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, drive_array_label, volume_template_id, drive_array_count, drive_size_mbytes_default, drive_array_expand_with_instance_array, instance_array_id, container_array_id, drive_array_change_id):
		self.drive_array_label = drive_array_label;
		self.volume_template_id = volume_template_id;
		self.drive_array_count = drive_array_count;
		self.drive_size_mbytes_default = drive_size_mbytes_default;
		self.drive_array_expand_with_instance_array = drive_array_expand_with_instance_array;
		self.instance_array_id = instance_array_id;
		self.container_array_id = container_array_id;
		self.drive_array_change_id = drive_array_change_id;


	"""
	The status of the deploy process.
	"""
	drive_array_deploy_status = None;

	"""
	The operation applied to the Drive array.
	"""
	drive_array_deploy_type = None;

	"""
	The Drive array's unique label is used to create the
	<code>drive_array_subdomain</code>. It is editable and can be used to call
	API functions.
	"""
	drive_array_label = None;

	"""
	Automatically created based on <code>drive_array_label</code>. It is a
	unique reference to the Drive array object.
	"""
	drive_array_subdomain = None;

	"""
	The ID of the Drive array which can be used instead of the
	<code>drive_array_label</code> or <code>drive_array_subdomain</code> when
	calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	drive_array_id = None;

	"""
	The volume template ID or name. At the moment, the available templates are
	<code>"ubuntu-14-04"</code>, <code>"ubuntu16-04"</code>,
	<code>"centos6-5"</code>, <code>"centos6-6"</code>,
	<code>"centos6-8"</code>, <code>"centos6-9"</code>,
	<code>"centos71v1"</code>, <code>"centos7-2"</code>, and
	<code>"centos7-3"</code>
	"""
	volume_template_id = None;

	"""
	"""
	drive_array_storage_type = None;

	"""
	The Drive count on the Drive array.
	"""
	drive_array_count = None;

	"""
	The capacity of each Drive.
	"""
	drive_size_mbytes_default = None;

	"""
	If true, the Drive array and the InstanceArray expand simultaneously.
	"""
	drive_array_expand_with_instance_array = None;

	"""
	The infrastructure ID to which the Drive array belongs.
	"""
	infrastructure_id = None;

	"""
	The InstanceArray ID to which the Drive array belongs.
	"""
	instance_array_id = None;

	"""
	The ContainerArray ID to which the Drive array belongs.
	"""
	container_array_id = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Drive array was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	drive_array_updated_timestamp = None;

	"""
	Reserved for GUI users.
	"""
	drive_array_gui_settings_json = None;

	"""
	License utilization type for the license.
	"""
	license_utilization_type = "subscription";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	drive_array_change_id = None;

	"""
	Drive array file system information
	"""
	drive_array_filesystem = None;
