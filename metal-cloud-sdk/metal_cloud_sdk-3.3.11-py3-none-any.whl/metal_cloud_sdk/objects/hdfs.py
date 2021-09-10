# -*- coding: utf-8 -*-

class HDFS(object):
	"""
	An object with the necessary data to connect through the WebHDFS protocol.
	"""

	def __init__(self):
		pass;


	"""
	The home directory of the Data Lake for the specific infrastructure ID.
	"""
	home_directory = None;

	"""
	The ID of the user.
	"""
	user_id = None;

	"""
	The port of the namenode.
	"""
	namenode_port = None;

	"""
	The URL of the namenode.
	"""
	namenode_url = None;

	"""
	An URL used to connect to the File System via WebHDFS. Enables HTTP
	operations. 
	"""
	webhdfs_url = None;

	"""
	The schema type
	"""
	type = None;
