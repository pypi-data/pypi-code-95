# -*- coding: utf-8 -*-

class SubnetReservation(object):
	"""
	Represents a reservation created with a specific Subnet prefix size.
	"""

	def __init__(self, subnet_prefix_size, subnet_type):
		self.subnet_prefix_size = subnet_prefix_size;
		self.subnet_type = subnet_type;


	"""
	Represents the user ID who has the reservation.
	"""
	user_id = None;

	"""
	Date and time when the reservation was created. Is an ISO 8601 timestamp
	using UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_created_timestamp = None;

	"""
	Number of months in a reservation cycle.
	"""
	resource_reservation_cycle_months = None;

	"""
	Number of months in a reservation installment cycle.
	"""
	resource_reservation_installment_cycle_months = None;

	"""
	Date and time when the reservation expires. Is an ISO 8601 timestamp using
	UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_end_timestamp = None;

	"""
	Is an ISO 8601 timestamp using UTC time. Example format:
	2013-11-29T13:00:01Z.
	"""
	resource_reservation_current_timestamp = None;

	"""
	Is an ISO 8601 timestamp using UTC time. Example format:
	2013-11-29T13:00:01Z.
	"""
	resource_reservation_installment_last_active_end_timestamp = None;

	"""
	Is an ISO 8601 timestamp using UTC time. Example format:
	2013-11-29T13:00:01Z.
	"""
	resource_reservation_next_timestamp = None;

	"""
	The cost of the reserved resource for a 30-day period.
	"""
	subnet_ip_count = None;

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
	subnet_reservation_id = None;

	"""
	Subnet prefix size, such as /30, /27, etc. For IPv4 subnets can be one of:
	<code>27</code>, <code>28</code>, <code>29</code>, <code>30</code>. For IPv6
	subnet can only be <code>64</code>.
	"""
	subnet_prefix_size = None;

	"""
	The type of the Subnet.
	"""
	subnet_type = None;

	"""
	All the <a:schema>SubnetReservationInstallment</a:schema> objects associated
	with the reservation.
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
