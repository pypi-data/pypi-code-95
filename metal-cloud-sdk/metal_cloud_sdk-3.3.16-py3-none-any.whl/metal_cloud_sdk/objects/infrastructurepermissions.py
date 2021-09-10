# -*- coding: utf-8 -*-

class InfrastructurePermissions(object):
	"""
	Contains information about how access permissions propagate to new servers.
	"""

	def __init__(self, infrastructure_user_allow_ssh_keys):
		self.infrastructure_user_allow_ssh_keys = infrastructure_user_allow_ssh_keys;


	"""
	If <code>true</code>, the user's SSH keys are added automatically to newly
	created Drives that use an existing public Linux template. Only owners or
	owner delegates can affect this setting.
	"""
	infrastructure_user_allow_ssh_keys = None;

	"""
	The schema type
	"""
	type = None;
