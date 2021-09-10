# -*- coding: utf-8 -*-

class AppSplunkInstance(object):
	"""
	Details about the Instance object specific to Splunk. The infromation
	presented here is obtained by interrogating the Splunk API. Backward
	compatibility object will not be ensured when the underlying Splunk API
	changes.
	"""

	def __init__(self):
		pass;


	"""
	The initial admin username on the instance.
	"""
	admin_username = None;

	"""
	The initial admin password on the instance.
	"""
	admin_initial_password = None;

	"""
	The admin interface URL.
	"""
	url = None;

	"""
	Percentage of time CPU is running in system mode and user mode.
	"""
	cpu_total_pct = None;

	"""
	Total physical memory available.
	"""
	mem_total_gb = None;

	"""
	Percentage of used physical memory.
	"""
	mem_used_pct = None;

	"""
	Globally unique identifier for this server.
	"""
	guid = None;

	"""
	Type of Splunk Enterprise license. Can be one of: <code>"Enterprise"</code>,
	<code>"Forwarder"</code>, <code>"Free"</code>, <code>"Invalid"</code>,
	<code>"Trial"</code>. After installation the license type is
	<code>"Trial"</code>.
	"""
	activeLicenseGroup = None;

	"""
	All the active keys for the current license.
	"""
	licenseKeys = None;

	"""
	Specifies the status of the license, which can be either <code>"OK"</code>
	or <code>"Expired"</code>.
	"""
	licenseState = None;

	"""
	Software version number.
	"""
	version = None;

	"""
	The total size of logs that can be indexed in one day using the current
	license.
	"""
	license_quota_gb = None;

	"""
	The percentage of the total size of logs which was used .
	"""
	license_used_pct = None;

	"""
	Total disk capacity. It might take a while until the property is populated.
	"""
	storage_capacity_gb = None;

	"""
	Percentage of used disk capacity. It might take a while until the property
	is populated.
	"""
	storage_used_pct = None;

	"""
	The ID of the instance associated with the node.
	"""
	instance_id = None;

	"""
	The label of the instance associated with the node.
	"""
	instance_label = None;

	"""
	The schema type
	"""
	type = None;
