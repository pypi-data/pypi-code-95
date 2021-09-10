# -*- coding: utf-8 -*-

class DriveArray(object):
	"""
	A DriveArray is a collection of storage devices mounted via iSCSI.
	"""

	def __init__(self):
		pass;


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
	<code>"ubuntu14-04"</code>, <code>"ubuntu16-04"</code>,
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
	drive_array_count = 1;

	"""
	The capacity of each Drive in MBytes.
	"""
	drive_size_mbytes_default = 40960;

	"""
	If true, the Drive array and the InstanceArray expand simultaneously. If not
	enough Drives are available, new Drives will be created automatically and
	attached.
	"""
	drive_array_expand_with_instance_array = True;

	"""
	The infrastructure ID to which the Drive array belongs.
	"""
	infrastructure_id = None;

	"""
	The InstanceArray ID to which the Drive array is attached.
	"""
	instance_array_id = None;

	"""
	The ContainerArray ID to which the Drive array is attached.
	"""
	container_array_id = None;

	"""
	The status of the Drive array.
	"""
	drive_array_service_status = None;

	"""
	The operation type, operation status and modified Drive array object.
	"""
	drive_array_operation = None;

	"""
	If not <code>null</code>, then the InstanceArray is part of the specified
	Cluster.
	"""
	cluster_id = None;

	"""
	If not <code>null</code>, then the InstanceArray is part of the specified
	ContainerCluster.
	"""
	container_cluster_id = None;

	"""
	"""
	cluster_role_group = "none";

	"""
	Reserved for GUI users.
	"""
	drive_array_gui_settings_json = "";

	"""
	ISO 8601 timestamp which holds the date and time when the Drive array was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	drive_array_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the Drive array was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	drive_array_updated_timestamp = "0000-00-00T00:00:00Z";

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

	"""
	List of tags representative for the DriveArray.
	"""
	drive_array_tags = [];
