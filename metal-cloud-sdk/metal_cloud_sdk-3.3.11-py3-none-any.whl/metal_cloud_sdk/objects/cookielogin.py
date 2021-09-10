# -*- coding: utf-8 -*-

class CookieLogin(object):
	"""
	Login session.
	"""

	def __init__(self, user_id_bsi):
		self.user_id_bsi = user_id_bsi;


	"""
	Contains null for not authenticated sessions.
	"""
	user_id_bsi = None;

	"""
	True if user_id_bsi contains an authenticated user ID.
	"""
	is_logged_in = None;

	"""
	The schema type.
	"""
	type = None;
