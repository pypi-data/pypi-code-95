# -*- coding: utf-8 -*-

class LicenseContract(object):
	"""
	An license contract represents a link between a client and a vendor for a
	license type.
	"""

	def __init__(self, license_contract_price_currency, license_contract_cycle_end_timestamp, license_contract_cycle_start_timestamp):
		self.license_contract_price_currency = license_contract_price_currency;
		self.license_contract_cycle_end_timestamp = license_contract_cycle_end_timestamp;
		self.license_contract_cycle_start_timestamp = license_contract_cycle_start_timestamp;


	"""
	The ID of the License Contract.
	"""
	license_contract_id = None;

	"""
	The owner's user ID.
	"""
	user_id = None;

	"""
	This property specifies if the license contract should be automatically
	renewed.
	"""
	license_contract_is_recurring = False;

	"""
	Total cost of a license contract.
	"""
	license_contract_price = 0;

	"""
	The currency of the license contract.
	"""
	license_contract_price_currency = None;

	"""
	It shows the status of the LicenseContract.
	"""
	license_contract_status = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license contract
	was updated. Example format: 2013-11-29T13:00:01Z.
	"""
	license_contract_updated_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license contract
	is activated. Example format: 2013-11-29T13:00:01Z.
	"""
	license_contract_activation_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when to send a notification
	before license contract ends. Example format: 2013-11-29T13:00:01Z.
	"""
	license_contract_before_end_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license contract
	was created. Example format: 2013-11-29T13:00:01Z.
	"""
	license_contract_created_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license contract
	cycle ends. Example format: 2013-11-29T13:00:01Z.
	"""
	license_contract_cycle_end_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license contract
	cycle starts. Example format: 2013-11-29T13:00:01Z.
	"""
	license_contract_cycle_start_timestamp = None;

	"""
	The number of months for a installment cycle.
	"""
	license_installment_cycle_months = 1;

	"""
	License type for the license contract.
	"""
	license_type = None;

	"""
	License vendor for this contract.
	"""
	license_vendor = None;

	"""
	License version for this contract.
	"""
	license_version = None;

	"""
	The schema type
	"""
	type = None;
