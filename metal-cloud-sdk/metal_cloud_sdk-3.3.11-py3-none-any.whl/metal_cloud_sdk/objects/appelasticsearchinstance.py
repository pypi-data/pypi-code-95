# -*- coding: utf-8 -*-

class AppElasticsearchInstance(object):
	"""
	Details about the Instance object specific to Elasticsearch. The information
	presented here is obtained by interrogating the Elasticsearch API. Backward
	compatibility object will not be ensured when the underlying Elasticsearch
	API changes.
	"""

	def __init__(self):
		pass;


	"""
	The user interface URL.
	"""
	ui_url = None;

	"""
	Percentage of time CPU is running in system mode and user mode. Being a
	multiprocessor system, the usage can be greater than 100%.
	"""
	cpu_usage_percent = None;

	"""
	Total physical memory available.
	"""
	memory_total_gb = None;

	"""
	Percentage of used physical memory.
	"""
	memory_used_percent = None;

	"""
	Total disk capacity. It might take a while until the property is populated.
	"""
	fs_memory_total_gb = None;

	"""
	Percentage of used disk capacity. It might take a while until the property
	is populated.
	"""
	fs_memory_used_gb = None;

	"""
	Software version number.
	"""
	version = None;

	"""
	The Elasticsearch node ID.
	"""
	node_id = None;

	"""
	The ID of the Instance associated with the node.
	"""
	instance_id = None;

	"""
	The label of the Instance associated with the node.
	"""
	instance_label = None;

	"""
	The schema type
	"""
	type = None;
