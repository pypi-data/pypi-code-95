# -*- coding: utf-8 -*-

class InfrastructureDeployBlocker(object):
	"""
	Contains the results of tests performed before commencing an Infrastructure
	deploy operation in order to identify reasons that would lead to it failing.
	"""

	def __init__(self):
		pass;


	"""
	"""
	instance = None;

	"""
	"""
	cluster = None;

	"""
	"""
	instanceArray = None;

	"""
	"""
	sshConnectivity = None;

	"""
	"""
	sshAuthentication = None;

	"""
	"""
	apiConnectivity = None;

	"""
	"""
	apiAuthentication = None;

	"""
	"""
	memoryUsageReport = None;

	"""
	"""
	missingInterfaces = None;

	"""
	"""
	saasVersion = None;

	"""
	"""
	errorMessage = None;

	"""
	The schema type
	"""
	type = None;
