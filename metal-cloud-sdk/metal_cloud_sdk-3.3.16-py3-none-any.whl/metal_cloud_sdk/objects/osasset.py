# -*- coding: utf-8 -*-

class OSAsset(object):
	"""
	An asset file used by a volume template for booting or installing an OS.
	"""

	def __init__(self, os_asset_filename, os_asset_file_mime):
		self.os_asset_filename = os_asset_filename;
		self.os_asset_file_mime = os_asset_file_mime;


	"""
	The ID of the OS asset.
	"""
	os_asset_id = None;

	"""
	Owner. Delegates of this user can manage this OSAsset as well. Null when
	this OSAsset is public.
	"""
	user_id_owner = None;

	"""
	The user which last updated the bundle.
	"""
	user_id_authenticated = None;

	"""
	Filename of the OS asset file.
	"""
	os_asset_filename = None;

	"""
	File size of the stored OS asset content. Null if os_asset_source_url is
	given.
	"""
	os_asset_file_size_bytes = None;

	"""
	File mime of the OS asset file.
	"""
	os_asset_file_mime = None;

	"""
	Stored contents in base 64.
	"""
	os_asset_contents_base64 = None;

	"""
	Original content sha256 hash as a lowercase hex string.
	"""
	os_asset_contents_sha256_hex = None;

	"""
	Usage of OS asset.
	"""
	os_asset_usage = None;

	"""
	URL from which to serve the file. If just absolute pathname, the file will
	be served from our repo. If a complete http(s) URL it will be used as is. If
	os_asset_contents_base64 is set this will be null.
	"""
	os_asset_source_url = None;

	"""
	Date and time of the OSAsset's creation.
	"""
	os_asset_created_timestamp = None;

	"""
	Date and time of the OSAsset's update.
	"""
	os_asset_updated_timestamp = None;

	"""
	List of tags representative for the OS Asset.
	"""
	os_asset_tags = [];

	"""
	The schema type.
	"""
	type = None;

	"""
	OSAsset blob id.
	"""
	os_asset_blob_id = None;
