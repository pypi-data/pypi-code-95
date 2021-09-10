
import os

from .PathPatternMatcher import PathPatternMatcher
from .PathPatternMatcherCollection import PathPatternMatcherCollection





_REGEX_REPLACEMENT_MAP = {
	"^": "\\^",
	"?": "?",
	"$": "\\$",
	".": "\\.",
	"+": "\\+",
	"|": "\\|",
	"(": "\\(",
	")": "\\)",
	"[": "\\[",
	"]": "\\]",
	"{": "\\{",
	"}": "\\}",
	"\\": "\\\\",
	"*": "[^/]*"
}


#
# Compile a path pattern.
#
# @return	PathPatternMatcher			The regex based pattern matcher
#
def compilePattern(sPattern:str, raiseExceptionOnError:bool = True) -> PathPatternMatcher:
	if not sPattern:
		if raiseExceptionOnError:
			raise Exception("No data!")
		else:
			return None

	assert isinstance(sPattern, str)

	sOrgPattern = sPattern

	# ----

	bMatchAbsolutePath = sPattern.startswith("/")
	if bMatchAbsolutePath:
		sPattern = sPattern[1:]

	#bMatchDirectoryOnly = False
	if sPattern.endswith("/"):
		# NOTE: for now we will not support directory matching (yet). This might change in future versions.
		#bMatchDirectoryOnly = True
		#sPattern = sPattern[:-1]
		raise Exception("Failed to compile pattern: " + repr(sOrgPattern))

	components = []
	sPatternParts = sPattern.split("/")

	for i, sPatternPart in enumerate(sPatternParts):
		bFirst = i == 0
		bLast = i == len(sPatternParts) - 1
		bAddSlash = True

		_temp = []
		if sPatternPart == "**":
			if bLast:
				_temp.append(".*")
			else:
				bAddSlash = False
				_temp.append("(.*/)?")
		else:
			i = 0
			while i < len(sPatternPart):
				p = sPatternPart[i]
				pNext = sPatternPart[i + 1] if i < len(sPatternPart) - 1 else None
				if (p == "*") and (pNext == "*"):
					# detected: "....***...."
					if raiseExceptionOnError:
						raise Exception("Failed to compile pattern: " + repr(sOrgPattern))
					else:
						return None
				repl = _REGEX_REPLACEMENT_MAP.get(p)
				if repl is not None:
					_temp.append(repl)
				else:
					_temp.append(p)
				i += 1

		if not _temp:
			# detected: "....//...."
			if raiseExceptionOnError:
				raise Exception("Failed to compile pattern: " + repr(sOrgPattern))
			else:
				return None

		if bAddSlash:
			_temp.append("/")

		components.extend(_temp)

	# we will likely have added a trailing slash
	if components[-1] == "/":
		del components[-1]

	ret = "".join(components) + "$"
	if bMatchAbsolutePath:
		return PathPatternMatcher(sOrgPattern, bMatchAbsolutePath, "^/" + ret)
	return PathPatternMatcher(sOrgPattern, bMatchAbsolutePath, "^" + ret)
#





def compileAllPatterns(patterns) -> PathPatternMatcherCollection:
	assert isinstance(patterns, (tuple, list))

	c = PathPatternMatcherCollection()
	for p in patterns:
		r = compilePattern(p)
		c.append(r)
	if not c:
		return None
	return c
#





