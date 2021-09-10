# -*- coding: utf-8 -*-

class SSHAlgorithms(object):
	"""
	SSH client options such as the host, port, user, password, private keys,
	etc. All properties support template-like variables; for example,
	${{instance_credentials_password}} may be used as value for the password
	property.
	"""

	def __init__(self, type):
		self.type = type;


	"""
	Key exchange algorithms.
	"""
	kex = None;

	"""
	Ciphers. Connecting to out of date SSH servers may require configuring this
	value. Included by default at the time of writing this (may change without
	notice): "aes128-ctr", "aes192-ctr", "aes256-ctr", "aes128-gcm",
	"aes128-gcm@openssh.com", "aes256-gcm", "aes256-gcm@openssh.com". Known to
	be deprecated values and not included by default: "aes128-cbc",
	"aes256-cbc", "3des-cbc"
	"""
	cipher = None;

	"""
	Server host key formats.
	"""
	serverHostKey = None;

	"""
	(H)MAC algorithms.
	"""
	hmac = None;

	"""
	Compression algorithms.
	"""
	compress = None;

	"""
	The schema type
	"""
	type = None;
