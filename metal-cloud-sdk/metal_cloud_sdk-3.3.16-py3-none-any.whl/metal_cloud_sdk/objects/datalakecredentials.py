# -*- coding: utf-8 -*-

class DataLakeCredentials(object):
	"""
	Information needed to connect to the HDFS file system.
	"""

	def __init__(self, hdfs, kerberos):
		self.hdfs = hdfs;
		self.kerberos = kerberos;


	"""
	Information needed to connect to HDFS.
	"""
	hdfs = None;

	"""
	Information needed for authentication with Kerberos SPNEGO.
	"""
	kerberos = None;

	"""
	HDFS login tutorial
	"""
	hdfs_login_tutorial_url = None;

	"""
	Data Lake command line tool tutorial
	"""
	data_lake_command_line_tool_documentation_url = None;

	"""
	The schema type
	"""
	type = None;
