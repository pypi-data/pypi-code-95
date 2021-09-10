


import typing
import os
import collections
import stat

from .IWalkIOAdapter import IWalkIOAdapter
from .ILocalDiskIOAdapter import ILocalDiskIOAdapter
from .PathPatternMatcherCollection import PathPatternMatcherCollection
from .PathPatternMatcher import PathPatternMatcher
from .pm import compilePattern, compileAllPatterns
from .Entry import Entry




def _cmpileEndExtend(existing, patternOrPatterns):
	if patternOrPatterns:
		if isinstance(patternOrPatterns, str):
			patterns = [ patternOrPatterns ]
		elif isinstance(patternOrPatterns, (tuple, list)):
			patterns = patternOrPatterns
		else:
			raise TypeError(str(type(patternOrPatterns)))

		r = compileAllPatterns(patterns)
		if r is not None:
			if existing is None:
				existing = PathPatternMatcherCollection()
			existing.extend(r)

	return existing
#








#
# Traverse directory trees.
#
# @param		*dirPaths							(required) Provide one or more (!) directories here to traverse.
# @param		str|str[] acceptDirPathPatterns		(optional)
# @param		str|str[] acceptFilePathPatterns	(optional)
# @param		str|str[] acceptLinkPathPatterns	(optional)
# @param		str|str[] ignorePathPatterns		(optional) If specfied these are patterns of files/directories/links to ignore. Patterns are relative to the base directory traversed.
# @param		str|str[] ignoreDirPathPatterns		(optional) If specfied these are patterns of directories to ignore. Patterns are relative to the base directory traversed.
# @param		str|str[] ignoreFilePathPatterns	(optional) If specfied these are patterns of files to ignore. Patterns are relative to the base directory traversed.
# @param		str|str[] ignoreLinkPathPatterns	(optional) If specfied these are patterns of links to ignore. Patterns are relative to the base directory traversed.
# @param		bool emitDirs						(optional) If `True` function `walk(..)` will emit directory entries. (This option is `True` by default.)
# @param		bool emitFiles						(optional) If `True` function `walk(..)` will emit file entries. (This option is `True` by default.)
# @param		bool emitLinks						(optional) If `True` function `walk(..)` will emit link entries. (This option is `True` by default.)
# @param		bool emitBaseDirs					(optional) If `True` function `walk(..)` will emit traversal root directory entries. (This option is `True` by default.)
# @param		bool recursive						(optional) If `True` function `walk(..)` will traverse recursively through the specified directory tree. (This option is `True` by default.)
# @param		bool sort							(optional) If `True` function `walk(..)` will sort all entries returns by name. (This option is `True` by default.)
# @param		bool emitErrorEntries				(optional) If `True` function `walk(..)` will emit error entries. If `false` exceptions are raised. (This option is `True` by default.)
# @param		type clazz							(optional) If a class is specified here instances of *this* class are instantiated instead of `Entry`.
# @return		Entry[]								Returns an iterator over <c>Entry</c> objects. Each <c>Entry</c> object
#
def walk(*dirPaths,
		acceptDirPathPatterns = None,
		acceptFilePathPatterns = None,
		acceptLinkPathPatterns = None,
		ignorePathPatterns = None,
		ignoreDirPathPatterns = None,
		ignoreFilePathPatterns = None,
		ignoreLinkPathPatterns = None,
		emitDirs:bool = True,
		emitFiles:bool = True,
		emitLinks:bool = True,
		emitBaseDirs:bool = True,
		recursive:bool = True,
		sort:bool = True,
		emitErrorEntries:bool = True,
		clazz = None,
		ioAdapter:IWalkIOAdapter = None,
	) -> typing.Iterator[Entry]:

	if clazz is None:
		clazz = Entry
	else:
		assert clazz.__class__ == type

	ignoreDirPathMatcher = None
	ignoreFilePathMatcher = None
	ignoreLinkPathMatcher = None

	if ignorePathPatterns:
		ignoreFilePathMatcher = PathPatternMatcherCollection()
		ignoreDirPathMatcher = PathPatternMatcherCollection()
		ignoreLinkPathMatcher = PathPatternMatcherCollection()

		if isinstance(ignorePathPatterns, str):
			ignorePathPatterns = [ ignorePathPatterns ]

		_temp = compileAllPatterns(ignorePathPatterns)
		ignoreFilePathMatcher.extend(_temp)
		ignoreDirPathMatcher.extend(_temp)
		ignoreLinkPathMatcher.extend(_temp)

	ignoreDirPathMatcher = _cmpileEndExtend(ignoreDirPathMatcher, ignoreDirPathPatterns)
	ignoreFilePathMatcher = _cmpileEndExtend(ignoreFilePathMatcher, ignoreFilePathPatterns)
	ignoreLinkPathMatcher = _cmpileEndExtend(ignoreLinkPathMatcher, ignoreLinkPathPatterns)

	acceptDirPathMatcher = None
	acceptFilePathMatcher = None
	acceptLinkPathMatcher = None

	acceptDirPathMatcher = _cmpileEndExtend(acceptDirPathMatcher, acceptDirPathPatterns)
	acceptFilePathMatcher = _cmpileEndExtend(acceptFilePathMatcher, acceptFilePathPatterns)
	acceptLinkPathMatcher = _cmpileEndExtend(acceptLinkPathMatcher, acceptLinkPathPatterns)

	# ----

	if ioAdapter is None:
		ioAdapter = ILocalDiskIOAdapter()
	_lstat = ioAdapter.lstatCallback()
	_listdir = ioAdapter.listdirCallback()

	# ----

	dirPaths2 = []
	for d in dirPaths:
		if isinstance(d, (list, tuple)):
			for d2 in d:
				assert isinstance(d2, str)
				# remove trailing slashes
				if d2.endswith("/") and (len(d2) > 1):
					d2 = d2[:-1]
				dirPaths2.append(d2)
		else:
			# remove trailing slashes
			if d.endswith("/") and (len(d) > 1):
				d = d[:-1]
			dirPaths2.append(d)

	for dirPath in dirPaths2:
		dirPath = os.path.abspath(dirPath)
		s = dirPath
		if not s.endswith(os.path.sep):
			s += os.path.sep
		removePathPrefixLen = len(s)
		dirsToGo = [ (dirPath, dirPath, removePathPrefixLen, emitBaseDirs) ]

		while dirsToGo:
			nextDirPath, baseDirPath, removePathPrefixLen, bEmitBaseDir = dirsToGo[0]
			del dirsToGo[0]

			if bEmitBaseDir:
				statResult = _lstat(baseDirPath)
				assert baseDirPath == nextDirPath			# ??? is this the case ???
				yield Entry._createRootDir(clazz, baseDirPath, statResult)

			try:
				allEntries = _listdir(nextDirPath)
			except Exception as ee:
				# can't process this directory
				if emitErrorEntries:
					fullPath = nextDirPath
					relPath = fullPath[removePathPrefixLen:]
					yield Entry._createReadDirError(clazz, baseDirPath, relPath, ee)
				else:
					raise
				continue

			if sort:
				allEntries = sorted(allEntries)

			for entry in allEntries:
				fullPath = os.path.join(nextDirPath, entry)
				relPath = fullPath[removePathPrefixLen:]
				try:
					statResult = _lstat(fullPath)
					if stat.S_ISDIR(statResult.st_mode):
						if ignoreDirPathMatcher and ignoreDirPathMatcher.matchAR(fullPath, relPath):
							continue

						if emitDirs:
							if acceptDirPathMatcher is None or acceptDirPathMatcher.matchAR(fullPath, relPath):
								yield Entry._createDir(clazz, baseDirPath, relPath, statResult)

						if recursive:
							dirsToGo.append((fullPath, baseDirPath, removePathPrefixLen, False))

					elif stat.S_ISLNK(statResult.st_mode):
						if ignoreLinkPathMatcher and ignoreLinkPathMatcher.matchAR(fullPath, relPath):
							continue

						if emitFiles:
							if acceptLinkPathMatcher is None or acceptLinkPathMatcher.matchAR(fullPath, relPath):
								yield Entry._createLink(clazz, baseDirPath, relPath, statResult)

					elif stat.S_ISREG(statResult.st_mode):
						if ignoreFilePathMatcher and ignoreFilePathMatcher.matchAR(fullPath, relPath):
							continue

						if emitFiles:
							if acceptFilePathMatcher is None or acceptFilePathMatcher.matchAR(fullPath, relPath):
								yield Entry._createFile(clazz, baseDirPath, relPath, statResult)

				except FileNotFoundError as ee:
					# we end here if entry was a link but the link target does not exist
					pass
#




