# -*- coding: utf-8 -*-

class AppClouderaInstance(object):
	"""
	Details about the Instance object specific to Cloudera. The information
	presented here is obtained by interrogating the Cloudera API. Backward
	compatibility object will not be ensured when the underlying Cloudera API
	changes.
	"""

	def __init__(self):
		pass;


	"""
	The name of the role. Optional when creating a role. If not specified, a
	name will be automatically generated for the role.
	"""
	name = None;

	"""
	The commission state of this role.
	"""
	commissionState = None;

	"""
	The high-level health status of this role.
	"""
	healthSummary = None;

	"""
	Link into the Cloudera Manager web UI for this specific role.
	"""
	roleUrl = None;

	"""
	The host IP address.
	"""
	ipAddress = None;

	"""
	The amount of physical RAM on this host, in bytes.
	"""
	totalPhysMemBytes = None;

	"""
	The ID of the Instance associated with the node
	"""
	instance_id = None;

	"""
	The label of the Instance associated with the node
	"""
	instance_label = None;

	"""
	The status of the instance.
	"""
	instance_service_status = None;

	"""
	The schema type
	"""
	type = None;
