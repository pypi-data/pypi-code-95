# -*- coding: utf-8 -*-

class DataLake(object):
	"""
	A DataLake is a network file system or distributed file system for holding
	large amounts of data.
	"""

	def __init__(self):
		pass;


	"""
	Read-only property which defaults to a value derived from the datacenter
	name. The datacenter is inherited from the parent infrastructure.
	"""
	data_lake_label = None;

	"""
	Automatically created based on <code>data_lake_label</code>. It is a unique
	reference to the DataLake object.
	"""
	data_lake_subdomain = None;

	"""
	The ID of the DataLake which can be used instead of the
	<code>data_lake_label</code> or <code>data_lake_subdomain</code> when
	calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	data_lake_id = None;

	"""
	File system or protocol type.
	"""
	data_lake_type = "hdfs";

	"""
	The infrastructure ID to which the DataLake belongs.
	"""
	infrastructure_id = None;

	"""
	The status of the DataLake.
	"""
	data_lake_service_status = None;

	"""
	Information needed to connect to the HDFS File System.
	"""
	data_lake_credentials = None;

	"""
	The operation type, operation status and modified DataLake object.
	"""
	data_lake_operation = None;

	"""
	Reserved for GUI users.
	"""
	data_lake_gui_settings_json = "";

	"""
	ISO 8601 timestamp which holds the date and time when the DataLake was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	data_lake_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the DataLake was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	data_lake_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	data_lake_change_id = None;
