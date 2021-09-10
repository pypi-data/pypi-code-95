# -*- coding: utf-8 -*-

class ReportResourceUtilizationSummary(object):
	"""
	Contains the total costs for servers, Drives, Subnets, internet traffic and
	server reservations.
	"""

	def __init__(self, resource_utilization, internet, resource_reservation_installments, infrastructure_ids, start_timestamp, end_timestamp):
		self.resource_utilization = resource_utilization;
		self.internet = internet;
		self.resource_reservation_installments = resource_reservation_installments;
		self.infrastructure_ids = infrastructure_ids;
		self.start_timestamp = start_timestamp;
		self.end_timestamp = end_timestamp;


	"""
	All the detailed costs for Drives, instances and Subnets.
	"""
	resource_utilization = None;

	"""
	All the detailed costs for internet traffic.
	"""
	internet = None;

	"""
	All the detailed costs for server type reservations.
	"""
	resource_reservation_installments = None;

	"""
	The infrastructure IDs for the involved infrastructures.
	"""
	infrastructure_ids = [];

	"""
	ISO 8601 timestamp which holds the start date and time for calculating the
	costs of the resource usage.
	"""
	start_timestamp = None;

	"""
	ISO 8601 timestamp which holds the end date and time for calculating the
	costs of the resource usage.
	"""
	end_timestamp = None;

	"""
	The schema type
	"""
	type = None;
