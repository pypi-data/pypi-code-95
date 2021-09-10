# -*- coding: utf-8 -*-

class Dataset(object):
	"""
	Datasets are sources of data, that can be imported in a DataLake
	"""

	def __init__(self, dataset_name, dataset_description, dataset_price, dataset_price_currency, dataset_tags, datacenter_name, dataset_source_display_name, dataset_maintainer_display_name, dataset_formats):
		self.dataset_name = dataset_name;
		self.dataset_description = dataset_description;
		self.dataset_price = dataset_price;
		self.dataset_price_currency = dataset_price_currency;
		self.dataset_tags = dataset_tags;
		self.datacenter_name = datacenter_name;
		self.dataset_source_display_name = dataset_source_display_name;
		self.dataset_maintainer_display_name = dataset_maintainer_display_name;
		self.dataset_formats = dataset_formats;


	"""
	The ID of the dataset
	"""
	dataset_id = None;

	"""
	The owner's user ID.
	"""
	user_id_owner = None;

	"""
	The version of the dataset
	"""
	dataset_version = None;

	"""
	The name of the dataset
	"""
	dataset_name = None;

	"""
	Long description for what the dataset contains
	"""
	dataset_description = None;

	"""
	The commercial license for the dataset
	"""
	dataset_license_type = None;

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
	The URL for the topmost dataset directory
	"""
	dataset_url = None;

	"""
	The datacenter in which the dataset is available
	"""
	datacenter_name = None;

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
	ISO 8601 timestamp which holds the date and time when the Dataset was last
	updated. Example format: 2013-11-29T13:00:01Z.
	"""
	dataset_updated_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Dataset was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	dataset_created_timestamp = None;

	"""
	The dataset size(for all formats), in megabytes.
	"""
	dataset_size_mbytes = 0;

	"""
	A dataset being published makes it available to users other than the
	maintainer
	"""
	dataset_published = False;

	"""
	The name of the dataset readme file
	"""
	dataset_readme_file_name = None;

	"""
	The size in bytes of the dataset readme file
	"""
	dataset_readme_file_size_bytes = None;

	"""
	The schema type.
	"""
	type = None;
