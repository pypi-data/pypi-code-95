# -*- coding: utf-8 -*-

class DataPackage(object):
	"""
	datapackage.json files store the metadata of a dataset
	"""

	def __init__(self, dataset_price, dataset_price_currency):
		self.dataset_price = dataset_price;
		self.dataset_price_currency = dataset_price_currency;


	"""
	The name of the dataset
	"""
	dataset_name = None;

	"""
	Long description for what the dataset contains
	"""
	dataset_description = None;

	"""
	Total cost of a dataset.
	"""
	dataset_price = None;

	"""
	The currency for the price of the dataset.
	"""
	dataset_price_currency = None;

	"""
	List of tags representative for the dataset.
	"""
	dataset_tags = [];

	"""
	The actual source of the data (not necessarily the maintainer)
	"""
	dataset_source_display_name = None;

	"""
	Maintainer name to be displayed in the UI
	"""
	dataset_maintainer_display_name = None;

	"""
	List of formats in which the dataset is available.
	"""
	dataset_formats = [];

	"""
	The schema type.
	"""
	type = None;
