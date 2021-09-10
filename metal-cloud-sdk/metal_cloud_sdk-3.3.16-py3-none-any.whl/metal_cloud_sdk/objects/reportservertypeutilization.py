# -*- coding: utf-8 -*-

class ReportServerTypeUtilization(object):
	"""
	Cost details for a server type reservation.
	"""

	def __init__(self, cost, cost_currency, server_type_name, server_type_reservation_id, created_timestamp, start_timestamp, end_timestamp):
		self.cost = cost;
		self.cost_currency = cost_currency;
		self.server_type_name = server_type_name;
		self.server_type_reservation_id = server_type_reservation_id;
		self.created_timestamp = created_timestamp;
		self.start_timestamp = start_timestamp;
		self.end_timestamp = end_timestamp;


	"""
	The costs of a server reservation for a period of time.
	"""
	cost = None;

	"""
	The currency used to calculate the costs.
	"""
	cost_currency = None;

	"""
	The name of the server type.
	"""
	server_type_name = None;

	"""
	The ID of the server type reservation.
	"""
	server_type_reservation_id = None;

	"""
	Date and time when the server reservation was created.
	"""
	created_timestamp = None;

	"""
	Date and time when the server reservation becomes active. It is an hour
	later than <code>created_timestamp</code>.
	"""
	start_timestamp = None;

	"""
	Date and time when the server reservation expires.
	"""
	end_timestamp = None;

	"""
	The schema type
	"""
	type = None;
