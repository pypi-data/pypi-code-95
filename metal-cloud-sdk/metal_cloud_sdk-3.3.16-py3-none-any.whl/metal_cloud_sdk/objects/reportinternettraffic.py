# -*- coding: utf-8 -*-

class ReportInternetTraffic(object):
	"""
	The Internet traffic.
	"""

	def __init__(self, download, upload):
		self.download = download;
		self.upload = upload;


	"""
	The downloaded data.
	"""
	download = None;

	"""
	The uploaded data.
	"""
	upload = None;

	"""
	The schema type
	"""
	type = None;
