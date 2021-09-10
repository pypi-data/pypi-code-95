# -*- coding: utf-8 -*-

class InfrastructureOperation(object):
	"""
	InfrastructureOperation contains information regarding the changes that are
	to be made to a product. Edit and deploy functions have to be called in
	order to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, infrastructure_label, datacenter_name):
		self.infrastructure_label = infrastructure_label;
		self.datacenter_name = datacenter_name;


	"""
	The status of the deploy process.
	"""
	infrastructure_deploy_status = None;

	"""
	The operation applied to the infrastructure.
	"""
	infrastructure_deploy_type = None;

	"""
	The infrastructure's unique subdomain label is used to create the
	<code>infrastructure_subdomain</code>. Can be used to call API functions.
	"""
	infrastructure_label = None;

	"""
	Automatically created based on <code>infrastructure_label</code>. It is a
	unique reference to the Infrastructure object.
	"""
	infrastructure_subdomain = None;

	"""
	If <code>null</code>, this property will default to the first array element
	returned by <code>datacenters()</code>. It is read-only for infrastructures
	with infrastructure_service_status = <code>SERVICE_STATUS_ACTIVE</code>.
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
	ISO 8601 timestamp which holds the date and time when the infrastructure was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	infrastructure_updated_timestamp = None;

	"""
	Reserved for GUI users.
	"""
	infrastructure_gui_settings_json = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	If the operation is ongoing, it uniquely identifies the current deploy
	operation. If the operation is finished, it uniquely identifies the deploy
	operation of the entire infrastructure, at the time of this change.
	"""
	infrastructure_deploy_id = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	infrastructure_change_id = None;

	"""
	Notifies the Sales team about additional customer private datacenter needs.
	"""
	infrastructure_private_datacenters_json = None;

	"""
	The subnet pool used on this infrastructure to allocate private IPs
	"""
	subnet_pool_lan = None;

	"""
	Contains the reserved LAN IP ranges on the infrastructure.
	"""
	infrastructure_reserved_lan_ip_ranges = [];

	"""
	Infrastructure description for supporting ProjectAPI feature.
	"""
	infrastructure_description = None;

	"""
	Object containing custom variables and variable overrides.
	"""
	infrastructure_custom_variables = {};
