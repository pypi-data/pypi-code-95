# -*- coding: utf-8 -*-

class ContainerStatus(object):
	"""
	A ContainerStatus contains the status of the Container.
	"""

	def __init__(self):
		pass;


	"""
	The phase of the Container.
	"""
	status_phase = None;

	"""
	A brief message that indicates details about the reason that led the
	Container into the current state.
	"""
	status_reason = None;

	"""
	A human readable message that indicates details about the reason that led
	the Container into the current state.
	"""
	status_message = None;

	"""
	RFC3339 timestamp which holds the date and time when the Container was
	started. Example format: 2013-11-29T13:00:01Z.
	"""
	status_started_timestamp = None;

	"""
	The public IP address of the host the Container was scheduled on in natural
	language.
	"""
	status_host_ip_public_human_readable = None;

	"""
	The Container private IP address in natural language.
	"""
	status_container_ip_private_human_readable = None;

	"""
	The schema type.
	"""
	type = None;
