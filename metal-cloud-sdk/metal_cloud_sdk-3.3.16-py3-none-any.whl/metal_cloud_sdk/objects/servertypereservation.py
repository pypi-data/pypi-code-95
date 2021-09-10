# -*- coding: utf-8 -*-

class ServerTypeReservation(object):
	"""
	Represents a reservation created for a specific server type.
	"""

	def __init__(self, user_id, server_type_id, datacenter_name):
		self.user_id = user_id;
		self.server_type_id = server_type_id;
		self.datacenter_name = datacenter_name;


	"""
	The user who owns and pays for the reservation.
	"""
	user_id = None;

	"""
	Date and time when the reservation was created. Is an ISO 8601 timestamp
	using UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_created_timestamp = None;

	"""
	Contract period size, which gets renewed automatically if this reservation
	is recurring.
	"""
	resource_reservation_cycle_months = 12;

	"""
	Billing cycle in months.
	"""
	resource_reservation_installment_cycle_months = 1;

	"""
	Date and time when the reservation expires. Is an ISO 8601 timestamp using
	UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_end_timestamp = None;

	"""
	The cost of the reserved resource for a 30-day period.
	"""
	resource_reservation_price = None;

	"""
	The currency used to calculate the price.
	"""
	resource_reservation_price_currency = None;

	"""
	If <code>true</code>, the reservation is automatically renewed for another
	cycle when reaching its expiration date.
	"""
	resource_reservation_recurring = True;

	"""
	Date and time when the reservation becomes active. It is an hour later than
	<code>resource_reservation_created_timestamp</code>. Is an ISO 8601
	timestamp using UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_start_timestamp = None;

	"""
	This value overwrites the on-demand price when costs are calculated. If it
	is 0, using this resource will register no on-demand costs.
	"""
	resource_utilization_price = None;

	"""
	The currency used to calculate the price for a single unit of time.
	"""
	resource_utilization_price_currency = None;

	"""
	The unit of time measured in seconds.
	"""
	resource_utilization_price_unit_seconds = None;

	"""
	The ID of the reservation.
	"""
	server_type_reservation_id = None;

	"""
	The ID of the reserved server type.
	"""
	server_type_id = None;

	"""
	All the <a:schema>ServerTypeReservationInstallment</a:schema> objects
	associated with the reservation.
	"""
	resource_reservation_installments = [];

	"""
	The status of the reservation.
	"""
	resource_reservation_status = None;

	"""
	The datacenter on which the reservation is made.
	"""
	datacenter_name = None;

	"""
	The user plan type based on wich the reservation is made.
	"""
	user_plan_type = "vanilla";

	"""
	The schema type
	"""
	type = None;
