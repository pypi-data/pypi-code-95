# -*- coding: utf-8 -*-

class ContainerArrayLivenessCheck(object):
	"""
	ContainerArray check to perform in order to asses the liveness of its
	Containers.
	"""

	def __init__(self, check_action_type, check_action):
		self.check_action_type = check_action_type;
		self.check_action = check_action;


	"""
	ContainerArrayLivenessCheck action type to perform.
	"""
	check_action_type = None;

	"""
	ContainerArrayLivenessCheck action to perform.
	"""
	check_action = None;

	"""
	Number of seconds after the Container has started before the
	ContainerArrayLivenessCheck is initiated.
	"""
	check_delay_seconds = 10;

	"""
	Time interval between consecutive ContainerArrayLivenessChecks in seconds.
	Minimum value is 1.
	"""
	check_interval_seconds = 10;

	"""
	Number of seconds after which the ContainerArrayLivenessCheck times out.
	Minimum value is 1.
	"""
	check_timeout_seconds = 1;

	"""
	Minimum consecutive failures for the ContainerArrayLivenessCheck to be
	considered failed after having succeeded. Minimum value is 1.
	"""
	check_failure_threshold = 3;

	"""
	The schema type.
	"""
	type = None;
