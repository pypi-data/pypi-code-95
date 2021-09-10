# -*- coding: utf-8 -*-

class ContainerArrayReadinessCheck(object):
	"""
	ContainerArray check to perform in order to asses the readiness or liveness
	of its Containers.
	"""

	def __init__(self, check_action_type, check_action):
		self.check_action_type = check_action_type;
		self.check_action = check_action;


	"""
	ContainerArrayReadinessCheck action type to perform.
	"""
	check_action_type = None;

	"""
	ContainerArrayReadinessCheck action to perform.
	"""
	check_action = None;

	"""
	Number of seconds after the Container has started before the
	ContainerArrayReadinessCheck is initiated.
	"""
	check_delay_seconds = 5;

	"""
	Time interval between consecutive ContainerArrayReadinessChecks in seconds.
	Minimum value is 1.
	"""
	check_interval_seconds = 10;

	"""
	Number of seconds after which the ContainerArrayReadinessCheck times out.
	Minimum value is 1.
	"""
	check_timeout_seconds = 1;

	"""
	Minimum consecutive successes for the ContainerArrayReadinessCheck to be
	considered successful after having failed. Minimum value is 1.
	"""
	check_success_threshold = 1;

	"""
	Minimum consecutive failures for the ContainerArrayReadinessCheck to be
	considered failed after having succeeded. Minimum value is 1.
	"""
	check_failure_threshold = 3;

	"""
	The schema type.
	"""
	type = None;
