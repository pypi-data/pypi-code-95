# -*- coding: utf-8 -*-

class SubnetReservationInstallment(object):
	"""
	Represents a cyclical installment of a reservation created with a specific
	Subnet prefix size.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the reservation.
	"""
	subnet_reservation_id = None;

	"""
	The ID of the reservation installment.
	"""
	subnet_reservation_installment_id = None;

	"""
	Date and time when the reservation installment was created. Is an ISO 8601
	timestamp using UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_installment_created_timestamp = None;

	"""
	Date and time when the reservation becomes active. Is an ISO 8601 timestamp
	using UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_installment_start_timestamp = None;

	"""
	Date and time when the reservation installment expires. Is an ISO 8601
	timestamp using UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	resource_reservation_installment_end_timestamp = None;

	"""
	The costs of all the reserved resources for the duration of the installment.
	"""
	resource_reservation_installment_price = None;

	"""
	The currency used to calculate the price.
	"""
	resource_reservation_installment_price_currency = None;

	"""
	The status of the reservation installment.
	"""
	resource_reservation_installment_status = None;

	"""
	The schema type
	"""
	type = None;
