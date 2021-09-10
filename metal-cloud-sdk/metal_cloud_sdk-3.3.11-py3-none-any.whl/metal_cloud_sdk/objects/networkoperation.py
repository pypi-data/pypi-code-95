# -*- coding: utf-8 -*-

class NetworkOperation(object):
	"""
	NetworkOperation contains information regarding the changes that are to be
	made to a product. Edit and deploy functions have to be called in order to
	apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, network_label, network_change_id):
		self.network_label = network_label;
		self.network_change_id = network_change_id;


	"""
	The status of the deploy process.
	"""
	network_deploy_status = None;

	"""
	The operation applied to the network.
	"""
	network_deploy_type = None;

	"""
	The network's label which is unique and it is used to form the
	<code>network_subdomain</code>. Can be used to call API functions.
	"""
	network_label = None;

	"""
	Automatically created based on <code>network_label</code>. It is a unique
	reference to the Network object.
	"""
	network_subdomain = None;

	"""
	Represents the ID of the network which can be used instead of the
	<code>network_label</code> or <code>network_subdomain</code> when calling
	the API functions.  It is automatically generated and cannot be edited.
	"""
	network_id = None;

	"""
	ISO 8601 timestamp which holds the date and time when the network was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	network_updated_timestamp = None;

	"""
	The network type.
	"""
	network_type = None;

	"""
	Reserved for GUI users.
	"""
	network_gui_settings_json = "";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	network_change_id = None;

	"""
	The VLAN ID allocated for this network.
	"""
	network_vlan_id = None;

	"""
	This property specify whether the allocation of the private IPS is done
	automatically or manually.
	"""
	network_lan_autoallocate_ips = False;
