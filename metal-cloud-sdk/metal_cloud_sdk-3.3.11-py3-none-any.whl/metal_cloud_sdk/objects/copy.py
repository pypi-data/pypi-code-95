# -*- coding: utf-8 -*-

class Copy(object):
	"""
	Source and destination of a SCP operation. The source may be of various
	types. SCP and HTTP requests are streamed so they are recommended as
	sources. The destination has to be a SCP resource.
	"""

	def __init__(self, source, destination, type):
		self.source = source;
		self.destination = destination;
		self.type = type;


	"""
	"""
	source = None;

	"""
	"""
	destination = None;

	"""
	Duration timeout in minutes.
	"""
	timeoutMinutes = 240;

	"""
	What to do if the destination already exists.
	"""
	ifDestinationAlreadyExists = "overwrite";

	"""
	The schema type
	"""
	type = None;
