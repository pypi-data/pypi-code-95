# -*- coding: utf-8 -*-

class License(object):
	"""
	"""

	def __init__(self, license_price_currency, license_start_timestamp):
		self.license_price_currency = license_price_currency;
		self.license_start_timestamp = license_start_timestamp;


	"""
	The ID of the License.
	"""
	license_id = None;

	"""
	The LicenseContract ID.
	"""
	license_contract_id = None;

	"""
	This property specifies if the license should be automatically renewed.
	"""
	license_is_recurring = False;

	"""
	Total cost of a license.
	"""
	license_price = 0;

	"""
	The currency of the license.
	"""
	license_price_currency = None;

	"""
	It shows the status of the license.
	"""
	license_status = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license was
	updated. Example format: 2013-11-29T13:00:01Z.
	"""
	license_updated_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license is
	activated. Example format: 2013-11-29T13:00:01Z.
	"""
	license_activation_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	license_created_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license cycle
	ends. Example format: 2013-11-29T13:00:01Z.
	"""
	license_end_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license cycle
	starts. Example format: 2013-11-29T13:00:01Z.
	"""
	license_start_timestamp = None;

	"""
	The number of months for a installment cycle.
	"""
	license_installment_cycle_months = 1;

	"""
	License type for the license.
	"""
	license_type = None;

	"""
	License utilization type for the license.
	"""
	license_utilization_type = "subscription";

	"""
	License vendor for this license.
	"""
	license_vendor = None;

	"""
	License version for this license.
	"""
	license_version = None;

	"""
	License properties.
	"""
	license_properties = None;

	"""
	The schema type
	"""
	type = None;
