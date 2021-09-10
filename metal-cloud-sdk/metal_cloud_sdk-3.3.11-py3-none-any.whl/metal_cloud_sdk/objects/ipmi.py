# -*- coding: utf-8 -*-

class IPMI(object):
	"""
	IPMI credentials. Intelligent Platform Management Interface is a set of
	computer interface specifications for an autonomous computer subsystem that
	provides management and monitoring capabilities independently of the host
	system's CPU, firmware (BIOS or UEFI) and operating system.
	"""

	def __init__(self):
		pass;


	"""
	IP address for the IPMI.
	"""
	ip_address = None;

	"""
	The IPMI version.
	"""
	version = None;

	"""
	The username for the IPMI.
	"""
	username = None;

	"""
	The initial password for the IPMI.
	"""
	initial_password = None;

	"""
	The schema type
	"""
	type = None;
