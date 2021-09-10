# -*- coding: utf-8 -*-

class AppVMwarevSphere(object):
	"""
	VMware vSphere cluster.
	"""

	def __init__(self, vsphere_worker, vsphere_master):
		self.vsphere_worker = vsphere_worker;
		self.vsphere_master = vsphere_master;


	"""
	"""
	vsphere_worker = [];

	"""
	"""
	vsphere_master = [];

	"""
	The admin username on the cluster.
	"""
	admin_username = None;

	"""
	The initial admin password on the cluster.
	"""
	admin_initial_password = None;

	"""
	Cluster software available versions.
	"""
	cluster_software_available_versions = [];

	"""
	The software version detected on the cluster.
	"""
	cluster_software_version = None;

	"""
	The schema type
	"""
	type = None;

	"""
	The vCenter Server Management URL.
	"""
	instance_vcenter_server_management = None;

	"""
	The vCenter Web Client URL.
	"""
	instance_vcenter_web_client = None;

	"""
	The vCenter Server Management username on the cluster.
	"""
	vcsa_username = None;

	"""
	The initial vCenter Server Management password on the cluster.
	"""
	vcsa_initial_password = None;
