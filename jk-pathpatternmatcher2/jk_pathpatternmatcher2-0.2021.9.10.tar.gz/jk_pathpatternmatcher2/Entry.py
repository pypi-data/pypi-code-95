


import typing
import os
import collections
import stat
if os.name != "nt":
	import pwd
	import grp

import jk_prettyprintobj





#
# @field	str fullPath			The absolute file path to the entry
# @field	str absBaseDirPath		The absolute directory path the search is based on
# @field	str relFilePath			The relative path to the entry (based on <c>baseDirPath</c>)
# @field	str dirPath				The directory the entry resides in
# @field	str name				The name the entry
# @field	str typeID				An entry type identifier:
#									* "d" for directory
#									* "f" for file
#									* "l" for symbolic link
#									* "e" for error in reading a directory
#
class Entry(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self,
			absBaseDirPath:str,
			relFilePath:str,
			typeID:str,
			mtime:float,
			uid:int,
			gid:int,
			size:int,
			mode:int,
			exception:Exception,
		):

		self.baseDirPath = absBaseDirPath
		self.relFilePath = relFilePath
		self.typeID = typeID
		self.mtime = mtime
		self.uid = uid
		self.gid = gid
		self.size = size
		self.mode = mode
		self.exception = exception
	#

	################################################################################################################################
	## Public Deprecated Properties
	################################################################################################################################

	#
	# This is the directory the current entry resides in, An absolute path is returned here.
	#
	@property
	def dirPath(self) -> str:
		if self.relFilePath == "":
			return self.baseDirPath
		else:
			return os.path.dirname(self.fullPath)
	#

	#
	# The name of this entry
	#
	@property
	def name(self) -> str:
		if self.relFilePath == "":
			return ""
		else:
			return os.path.basename(self.relFilePath)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def relDirPath(self) -> str:
		if self.relFilePath == "":
			return self.baseDirPath
		else:
			return os.path.dirname(self.relFilePath)
	#

	#
	# The name of this entry
	#
	@property
	def fileName(self) -> str:
		if self.relFilePath == "":
			return ""
		else:
			return os.path.basename(self.relFilePath)
	#

	#
	# Returns the link text stored at the link if this is a link. If this entry is not a link `None` is returned.
	#
	@property
	def linkText(self) -> typing.Union[str,None]:
		if self.typeID == "l":
			return os.readlink(self.fullPath)
		else:
			return None
	#

	#
	# This is the absolute path of this entry.
	#
	@property
	def fullPath(self) -> str:
		if self.relFilePath == "":
			return self.baseDirPath
		else:
			return os.path.join(self.baseDirPath, self.relFilePath)
	#

	#
	# `True` if this is a base directory (and base directory only).
	#
	@property
	def isBaseDir(self) -> bool:
		return self.relFilePath == ""
	#

	#
	# `True` if this is an error entry.
	#
	@property
	def isError(self) -> bool:
		return self.exception is not None
	#

	#
	# The name of the owning group
	#
	@property
	def group(self) -> typing.Union[str,None]:
		if os.name == "nt":
			return None
		x = grp.getgrgid(self.gid)
		if x:
			return x.gr_name
		else:
			return None
	#

	#
	# The name of the owning user
	#
	@property
	def user(self) -> typing.Union[str,None]:
		if os.name == "nt":
			return None
		x = pwd.getpwuid(self.uid)
		if x:
			return x.pw_name
		else:
			return None
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> list:
		return [
			"fullPath",
			"baseDirPath",
			"relFilePath",
			"dirPath",
			"name",
			"typeID",
			"size",
			"mtime",
			"uid",
			"gid",
			"mode",
			"linkText",
			"exception",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __repr__(self):
		if self.exception:
			return "<{}({}, {}, {})>".format(self.__class__.__name__, self.typeID, repr(self.relFilePath), repr(self.exception))
		else:
			return "<{}({}, {})>".format(self.__class__.__name__, self.typeID, repr(self.relFilePath))
	#

	def __str__(self):
		if self.exception:
			return "<{}({}, {}, {})>".format(self.__class__.__name__, self.typeID, repr(self.relFilePath), repr(self.exception))
		else:
			return "<{}({}, {})>".format(self.__class__.__name__, self.typeID, repr(self.relFilePath))
	#

	################################################################################################################################
	## Static Helper Methods
	################################################################################################################################

	@staticmethod
	def _createDir(clazz, baseDirPath:str, relFilePath:str, statResult:os.stat_result):
		assert stat.S_ISDIR(statResult.st_mode)

		return clazz(
			baseDirPath,
			relFilePath,
			"d",
			statResult.st_mtime,
			statResult.st_uid,
			statResult.st_gid,
			statResult.st_size,
			statResult.st_mode,
			None)
	#

	@staticmethod
	def _createLink(clazz, baseDirPath:str, relFilePath:str, statResult:os.stat_result):
		assert stat.S_ISLNK(statResult.st_mode)

		return clazz(
			baseDirPath,
			relFilePath,
			"l",
			statResult.st_mtime,
			statResult.st_uid,
			statResult.st_gid,
			statResult.st_size,
			statResult.st_mode,
			None)
	#

	@staticmethod
	def _createReadDirError(clazz, baseDirPath:str, relFilePath:str, ee):
		return clazz(
			baseDirPath,
			relFilePath,
			"e",
			None,
			None,
			None,
			None,
			None,
			ee)
	#

	@staticmethod
	def _createRootDir(clazz, fullPath:str, statResult:os.stat_result):
		assert stat.S_ISDIR(statResult.st_mode)

		return clazz(
			fullPath,
			"",
			"d",
			statResult.st_mtime,
			statResult.st_uid,
			statResult.st_gid,
			statResult.st_size,
			statResult.st_mode,
			None)
	#

	@staticmethod
	def _createFile(clazz, baseDirPath:str, relFilePath:str, statResult:os.stat_result):
		assert stat.S_ISREG(statResult.st_mode)

		return clazz(
			baseDirPath,
			relFilePath,
			"f",
			statResult.st_mtime,
			statResult.st_uid,
			statResult.st_gid,
			statResult.st_size,
			statResult.st_mode,
			None)
	#

#



#Entry = collections.namedtuple("Entry", [ "fullPath", "baseDirPath", "relFilePath", "dirPath", "name", "type", "mtime", "uid", "gid", "size", "linkText" ])





