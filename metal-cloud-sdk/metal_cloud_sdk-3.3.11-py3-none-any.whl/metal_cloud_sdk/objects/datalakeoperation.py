# -*- coding: utf-8 -*-

class DataLakeOperation(object):
	"""
	DataLakeOperation contains information regarding the changes that are to be
	made to a product. Edit and deploy functions have to be called in order to
	apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, data_lake_label, data_lake_change_id):
		self.data_lake_label = data_lake_label;
		self.data_lake_change_id = data_lake_change_id;


	"""
	The status of the deploy process.
	"""
	data_lake_deploy_status = None;

	"""
	The operation applied to the DataLake.
	"""
	data_lake_deploy_type = None;

	"""
	The DataLake's unique label is used to create the
	<code>data_lake_subdomain</code>. It is editable and can be used to call API
	functions.
	"""
	data_lake_label = None;

	"""
	Automatically created based on <code>data_lake_label</code>. It is a unique
	reference to the DataLake object..
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
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	data_lake_change_id = None;
