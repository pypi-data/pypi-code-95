# -*- coding: utf-8 -*-

class AnsibleBundle(object):
	"""
	An Ansible bundle contains an Ansible project as a single archive file,
	usually .zip
	"""

	def __init__(self, ansible_bundle_archive_filename, type):
		self.ansible_bundle_archive_filename = ansible_bundle_archive_filename;
		self.type = type;


	"""
	For example: ansible_install_some_stuff.zip
	"""
	ansible_bundle_archive_filename = None;

	"""
	ZIP archive in base64 format.
	"""
	ansible_bundle_archive_contents_base64 = None;

	"""
	The schema type
	"""
	type = None;
