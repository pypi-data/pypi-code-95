# -*- coding: utf-8 -*-

class ContainerArrayActionExecuteCommand(object):
	"""
	ContainerArray action that executes a command on the Containers to asses
	their readiness or liveness.
	"""

	def __init__(self, action_command):
		self.action_command = action_command;


	"""
	Command to execute on the Containers. The command is not executed using a
	shell and the root of each Container (/) is used as working directory. An
	exit status of 0 is treated as healthy and non-zero as unhealthy
	"""
	action_command = [];

	"""
	The schema type.
	"""
	type = None;
