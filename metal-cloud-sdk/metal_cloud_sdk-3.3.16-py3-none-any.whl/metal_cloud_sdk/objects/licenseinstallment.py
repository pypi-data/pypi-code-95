# -*- coding: utf-8 -*-

class LicenseInstallment(object):
	"""
	"""

	def __init__(self, license_installment_price_currency, license_installment_end_timestamp, license_installment_start_timestamp):
		self.license_installment_price_currency = license_installment_price_currency;
		self.license_installment_end_timestamp = license_installment_end_timestamp;
		self.license_installment_start_timestamp = license_installment_start_timestamp;


	"""
	The ID of the LicenseInstallment.
	"""
	license_installment_id = None;

	"""
	The License ID.
	"""
	license_id = None;

	"""
	Total cost of a license installment.
	"""
	license_installment_price = 0;

	"""
	The currency of the license installment.
	"""
	license_installment_price_currency = None;

	"""
	It shows the status of the license installment.
	"""
	license_installment_status = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license
	installment was created. Example format: 2013-11-29T13:00:01Z.
	"""
	license_installment_created_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license
	installment cycle ends. Example format: 2013-11-29T13:00:01Z.
	"""
	license_installment_end_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the license
	installment cycle starts. Example format: 2013-11-29T13:00:01Z.
	"""
	license_installment_start_timestamp = None;

	"""
	The label of the license installment.
	"""
	license_installment_label = None;

	"""
	License properties.
	"""
	license_properties = None;

	"""
	The schema type
	"""
	type = None;
