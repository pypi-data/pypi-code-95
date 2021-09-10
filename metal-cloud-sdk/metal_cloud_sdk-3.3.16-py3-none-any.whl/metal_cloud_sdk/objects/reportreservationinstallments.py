# -*- coding: utf-8 -*-

class ReportReservationInstallments(object):
	"""
	All the detailed costs for server reservations.
	"""

	def __init__(self, server_types):
		self.server_types = server_types;


	"""
	<a:schema>ReportServerTypeUtilization</a:schema> objects. The costs for all
	the servers.
	"""
	server_types = [];

	"""
	The schema type
	"""
	type = None;
