# -*- coding: utf-8 -*-

class ReservedLANIPRange(object):
	"""
	A reserved LAN IP range.
	"""

	def __init__(self, reserved_range_start_human_readable, reserved_range_end_human_readable):
		self.reserved_range_start_human_readable = reserved_range_start_human_readable;
		self.reserved_range_end_human_readable = reserved_range_end_human_readable;


	"""
	The start address of the reserved LAN IP range.
	"""
	reserved_range_start_human_readable = None;

	"""
	The end address of the reserved LAN IP range.
	"""
	reserved_range_end_human_readable = None;

	"""
	Description regarding the use of the reserved range.
	"""
	reserved_range_description = None;

	"""
	The schema type.
	"""
	type = None;
