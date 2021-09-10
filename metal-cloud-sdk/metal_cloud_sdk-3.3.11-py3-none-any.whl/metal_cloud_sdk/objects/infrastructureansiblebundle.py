# -*- coding: utf-8 -*-

class InfrastructureAnsibleBundle(object):
	"""
	An Infrastructure Ansible bundle is an association of an AnsibleBundle, an
	Infrastructure and a run level priority index.
	"""

	def __init__(self, infrastructure_ansible_bundle_id, ansible_bundle_id, infrastructure_id, infrastructure_deploy_custom_stage_type, infrastructure_ansible_bundle_run_level):
		self.infrastructure_ansible_bundle_id = infrastructure_ansible_bundle_id;
		self.ansible_bundle_id = ansible_bundle_id;
		self.infrastructure_id = infrastructure_id;
		self.infrastructure_deploy_custom_stage_type = infrastructure_deploy_custom_stage_type;
		self.infrastructure_ansible_bundle_run_level = infrastructure_ansible_bundle_run_level;


	"""
	Unique Infrastructure, AnsibleBundle and run level index association ID.
	"""
	infrastructure_ansible_bundle_id = None;

	"""
	Represents an <a:schema>AnsibleBundle</a:schema>.
	"""
	ansible_bundle_id = None;

	"""
	Represents an <a:schema>Infrastructure</a:schema>
	"""
	infrastructure_id = None;

	"""
	"""
	infrastructure_deploy_custom_stage_type = None;

	"""
	Run priority index. 0 runs first. If multiple AnsibleBundles are on the same
	priority they run in parallel.
	"""
	infrastructure_ansible_bundle_run_level = None;

	"""
	Unstructured JSON.
	"""
	infrastructure_ansible_runner_output_json = None;

	"""
	The schema type
	"""
	type = None;
