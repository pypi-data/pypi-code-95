# -*- coding: utf-8 -*-

class Kerberos(object):
	"""
	An object with the required information to obtain the authentication ticket
	from Kerberos SPNEGO.
	"""

	def __init__(self, username):
		self.username = username;


	"""
	A user's account ID prefixed with the letter "k". For example:
	<code>k123</code>.
	"""
	username = None;

	"""
	Users may log in using their account password, as the DataLake HDFS Kerberos
	service is integrated with Metal Cloud (also for admin rights). This will
	always be <code>null</code>. Reserved for future use.
	"""
	initial_password = None;

	"""
	The Kerberos realm. 
	"""
	realm = None;

	"""
	Schema type.
	"""
	type = None;
