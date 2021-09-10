# -*- coding: utf-8 -*-

class Datacenter(object):
	"""
	Datacenter with physical resources which may be allocated to
	infrastructures.
	"""

	def __init__(self, datacenter_name, datacenter_display_name):
		self.datacenter_name = datacenter_name;
		self.datacenter_display_name = datacenter_display_name;


	"""
	The ID of the datacenter.
	"""
	datacenter_id = None;

	"""
	Uniquely identifies a datacenter.
	"""
	datacenter_name = None;

	"""
	Uniquely identifies the datacenter's parent.
	"""
	datacenter_name_parent = None;

	"""
	The owner's user ID. <code>Null</code> represents a publicly available
	datacenter. If a user ID is specified, the datacenter is private.
	"""
	user_id = None;

	"""
	Datacenter name for user interfaces.
	"""
	datacenter_display_name = None;

	"""
	Default datacenter for some internal logic.
	"""
	datacenter_is_master = False;

	"""
	Infrastructures and some resources are read-only for API requests while the
	parent datacenter is in maintenance mode.
	"""
	datacenter_is_maintenance = False;

	"""
	"""
	datacenter_type = "metal_cloud";

	"""
	ISO 8601 timestamp which holds the date and time when the datacenter was
	created through the API. Example format: 2013-11-29T13:00:01Z.
	"""
	datacenter_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the datacenter was
	created through the API. Example format: 2013-11-29T13:00:01Z.
	"""
	datacenter_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	True for datacenters which are under construction, beeing phased out, are to
	be avoided temporarily, or no longer exist.
	"""
	datacenter_hidden = False;

	"""
	List of tags representative for the Datacenter.
	"""
	datacenter_tags = [];

	"""
	The schema type
	"""
	type = None;
