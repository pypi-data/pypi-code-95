# -*- coding: utf-8 -*-

class SSHKey(object):
	"""
	Represents a SSH key added by a user
	"""

	def __init__(self):
		pass;


	"""
	An ID to represent the SSH key
	"""
	user_ssh_key_id = None;

	"""
	The ID of the user to which the SSH key belongs.
	"""
	user_id = None;

	"""
	A public key in OpenSSH format.
	"""
	user_ssh_key = None;

	"""
	Represents the date and time when the SSH key was created in ISO-8601, UTC
	timezone format.
	"""
	user_ssh_key_created_timestamp = None;

	"""
	The SSH key status.
	"""
	user_ssh_key_status = "active";

	"""
	The schema type
	"""
	type = None;
