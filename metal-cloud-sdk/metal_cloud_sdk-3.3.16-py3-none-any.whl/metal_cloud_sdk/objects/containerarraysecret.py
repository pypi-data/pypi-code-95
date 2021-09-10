# -*- coding: utf-8 -*-

class ContainerArraySecret(object):
	"""
	ContainerArray sensitive data to be stored encrypted and made available to
	the containers in plaintext.
	"""

	def __init__(self, secret_name, secret_data_base64):
		self.secret_name = secret_name;
		self.secret_data_base64 = secret_data_base64;


	"""
	Secret name.
	"""
	secret_name = None;

	"""
	Base64 encoded plaintext data.
	"""
	secret_data_base64 = None;

	"""
	The schema type.
	"""
	type = None;
