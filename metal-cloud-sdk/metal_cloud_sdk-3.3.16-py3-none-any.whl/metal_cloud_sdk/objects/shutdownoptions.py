# -*- coding: utf-8 -*-

class ShutdownOptions(object):
	"""
	Configures soft shutdown timeout options and gives a chance to allow or
	disallow hard shutdowns. Note that the operating systems must honor ACPI
	commands.
	"""

	def __init__(self, hard_shutdown_after_timeout, attempt_soft_shutdown):
		self.hard_shutdown_after_timeout = hard_shutdown_after_timeout;
		self.attempt_soft_shutdown = attempt_soft_shutdown;


	"""
	The timeout can be configured with this object's
	<code>soft_shutdown_timeout_seconds</code> property. If <code>false</code>,
	the <code>infrastructure_deploy()</code> call will hang if at least a
	required server is still powered on. The servers may be powered off manually
	using <code>instance_server_power_set()</code>.
	"""
	hard_shutdown_after_timeout = None;

	"""
	An ACPI soft shutdown command will be sent to corresponding servers. If
	false, a hard shutdown is executed.
	"""
	attempt_soft_shutdown = None;

	"""
	When the timeout expires, if <code>hard_shutdown_after_timeout</code> is
	<code>true</code>, then a hard power off will be attempted. Specifying a
	long timeout such as 1 day will block edits or deploying other new edits on
	infrastructure elements until the timeout expires or the servers are powered
	off. The servers may be powered off manually using
	<code>instance_server_power_set()</code>.
	"""
	soft_shutdown_timeout_seconds = 120;

	"""
	The schema type
	"""
	type = None;
