# -*- coding: utf-8 -*-

class Snapshot(object):
	"""
	A snapshot of a drive created at a specific time.
	"""

	def __init__(self):
		pass;


	"""
	The snapshot's unique label is formed based on the <code>snapshot_id</code>
	and the <code>snapshot_created_timestamp</code>.
	"""
	drive_snapshot_label = None;

	"""
	The ID of the snapshot.
	"""
	drive_snapshot_id = None;

	"""
	The ID of the Drive after which the snapshot was created.
	"""
	drive_id = None;

	"""
	Date and time when the drive snapshot was created. An ISO 8601 timestamp
	showing UTC time. Example format: 2013-11-29T13:00:01Z.
	"""
	drive_snapshot_created_timestamp = None;

	"""
	The schema type
	"""
	type = None;
