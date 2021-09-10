# -*- coding: utf-8 -*-

class Infrastructure(object):
	"""
	An infrastructure is the parent object for InstanceArrays, Instances,
	Clusters, Networks, Subnets, DriveArrays, Drives and DataLakes and their
	relationships.
	"""

	def __init__(self):
		pass;


	"""
	The infrastructure's unique label is used to create the
	<code>infrastructure_subdomain</code>. Can be used to call API functions.
	"""
	infrastructure_label = None;

	"""
	"""
	infrastructure_experimental_priority = None;

	"""
	Automatically created based on <code>infrastructure_label</code>. It is a
	unique reference to the Infrastructure object.
	"""
	infrastructure_subdomain = None;

	"""
	Read-only for infrastructures with infrastructure_service_status =
	<code>SERVICE_STATUS_ACTIVE</code>. Use <code>datacenters()</code> to obtain
	a list of possible values.
	"""
	datacenter_name = None;

	"""
	The ID of the infrastructure which can be used instead of the
	<code>infrastructure_label</code> when calling the API functions.
	"""
	infrastructure_id = None;

	"""
	The owner's user ID.
	"""
	user_id_owner = None;

	"""
	The owner's email.
	"""
	user_email_owner = None;

	"""
	Reserved for GUIs.
	"""
	infrastructure_touch_unixtime = None;

	"""
	The status of the infrastructure.
	"""
	infrastructure_service_status = None;

	"""
	The operation type, operation status and modified Infrastructure object.
	"""
	infrastructure_operation = None;

	"""
	ISO 8601 timestamp which holds the date and time when the infrastructure was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	infrastructure_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the infrastructure was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	infrastructure_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	Reserved for GUI users.
	"""
	infrastructure_gui_settings_json = "";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	infrastructure_change_id = None;

	"""
	The deploy which resulted in the currently provisioned state.
	"""
	infrastructure_deploy_id = None;

	"""
	Notifies the Sales team about additional customer private datacenter needs.
	"""
	infrastructure_private_datacenters_json = None;

	"""
	This property is used to prevent edits, reverts and deploys on the
	infrastructure.
	"""
	infrastructure_design_is_locked = False;

	"""
	Infrastructure holding independent instances.
	"""
	infrastructure_is_automanaged = False;

	"""
	The subnet pool used on this infrastructure to allocate private IPs
	"""
	subnet_pool_lan = None;

	"""
	Contains the reserved LAN IP ranges on the infrastructure.
	"""
	infrastructure_reserved_lan_ip_ranges = [];

	"""
	List of tags representative for the Infrastructure.
	"""
	infrastructure_tags = [];

	"""
	Infrastructure description for supporting ProjectAPI feature.
	"""
	infrastructure_description = None;

	"""
	Object containing custom variables and variable overrides.
	"""
	infrastructure_custom_variables = {};
