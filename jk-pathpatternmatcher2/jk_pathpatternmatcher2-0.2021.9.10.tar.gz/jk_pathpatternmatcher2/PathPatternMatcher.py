




import os
import re

import jk_typing





#
# This is a matcher to check if a single path matches the pattern.
#
class PathPatternMatcher(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	# @param		str orgPattern			The original pattern this matcher has been compiled from
	# @param		bool bAbsolute			This matcher only matches absolute paths
	# @param		str sRegex				The regular expression string compiled from the pattern
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self, orgPattern:str, bAbsolute:bool, sRegex:str):
		self.__orgPattern = orgPattern
		self.__bAbsolute = bAbsolute
		self.__sRegex = sRegex
		self.__r = re.compile(sRegex)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def regexPattern(self) -> str:
		return self.__sRegex
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def matchAR(self, fullPath:str, relPath:str) -> bool:
		if fullPath is None:
			raise Exception("This pattern matches absolute paths, therefore please specify an absolute path as a candidate for matching!")
		else:
			assert isinstance(fullPath, str)

		assert isinstance(relPath, str)
		if os.path.isabs(relPath):
			raise Exception("The specified path should be a relative path!")

		# ----

		if self.__bAbsolute:
			ret = self.__r.match(fullPath) is not None
		else:
			ret = self.__r.match(relPath) is not None

		# print("-- check:", repr(self.__orgPattern), repr(self.__sRegex), repr(s), repr(fullPath), repr(relPath), "=>", ("true" if ret else "false"))
		return ret
	#

	def match(self, relPath:str) -> bool:
		if self.__bAbsolute:
			raise Exception("This pattern matches absolute paths! Therefore match(..) is not suitable for this purpose!")

		if os.path.isabs(relPath):
			raise Exception("The specified path should be a relative path!")

		# ----

		ret = self.__r.match(relPath) is not None

		# print("-- check:", repr(self.__orgPattern), repr(self.__sRegex), repr(s), repr(fullPath), repr(relPath), "=>", ("true" if ret else "false"))
		return ret
	#

	def __str__(self):
		return "<PathPatternMatcher(" + repr(self.__orgPattern) + ")>"
	#

	def __repr__(self):
		return "<PathPatternMatcher(" + repr(self.__orgPattern) + ")>"
	#

#










