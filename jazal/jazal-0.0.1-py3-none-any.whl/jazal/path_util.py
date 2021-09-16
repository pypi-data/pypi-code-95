"""
The present module contains functions meant to help handling file paths, which
must be provided as pathlib.Path objects. This module follows Pathlib's vision
of file extensions as lists of suffixes starting with a '.'. However, in this
module, a file's stem is defined as its name without the extension while in
Pathlib, the stem is the file name without the last suffix.
"""


def extension_to_str(path):
	"""
	Concatenates the suffixes that make the extension of the given path.

	Args:
		path (pathlib.Path): the path whose extension is needed

	Returns:
		str: the path's extension as one string
	"""
	return "".join(path.suffixes)


def get_file_stem(path):
	"""
	Provides the stem of the file that a path points to.

	Args:
		path (pathlib.Path): the file path whose stem is needed

	Returns:
		str: the file's stem
	"""
	file_stem = path.name

	suffixes = path.suffixes
	if len(suffixes) > 0:
		exten_index = file_stem.index(suffixes[0])
		file_stem = file_stem[:exten_index]

	return file_stem


def make_altered_name(path, before_stem=None, after_stem=None, extension=None):
	"""
	Creates a file name by adding a string to the beginning and/or the end of
	a file path's stem and appending an extension to the new stem. If
	before_stem and after_stem are None, the new stem is identical to path's
	stem. This function does not change the given path. Use make_altered_stem
	instead if you do not want to append an extension.

	Args:
		path (pathlib.Path): the file path that provides the original name
		before_stem (str): the string to add to the beginning of the path's
			stem. If it is None, nothing is added to the stem's beginning.
			Defaults to None.
		after_stem (str): the string to add to the end of the path's stem. If
			it is None, nothing is added to the stem's end. Defaults to None.
		extension (str): the extension to append to the new stem in order to
			make the name. Each suffix must be such as those returned by
			pathlib.Path's property suffixes. If None, the extension of
			argument path is appended. Defaults to None.

	Returns:
		str: a new file name with the specified additions
	"""
	stem = make_altered_stem(path, before_stem, after_stem)

	if extension is None:
		name = stem + extension_to_str(path)
	else:
		name = stem + extension

	return name


def make_altered_path(path, before_stem=None, after_stem=None, extension=None):
	"""
	Creates a file path by adding a string to the beginning and/or the end of
	a file path's stem and appending an extension to the new stem. If
	before_stem and after_stem are None, the new stem is identical to path's
	stem. This function does not change the given path.

	Args:
		path (pathlib.Path): the file path of which an altered form is needed
		before_stem (str): the string to add to the beginning of the path's
			stem. If it is None, nothing is added to the stem's beginning.
			Defaults to None.
		after_stem (str): the string to add to the end of the path's stem. If
			it is None, nothing is added to the stem's end. Defaults to None.
		extension (str): the extension to append to the new stem in order to
			make the name. Each suffix must be such as those returned by
			pathlib.Path's property suffixes. If None, the extension of
			argument path is appended. Defaults to None.

	Returns:
		pathlib.Path: a new file path with the specified additions
	"""
	name = make_altered_name(path, before_stem, after_stem, extension)
	return path.parents[0]/name


def make_altered_stem(path, before_stem=None, after_stem=None):
	"""
	Creates a file stem by adding a string to the beginning and/or the end
	of a file path's stem. If before_stem and after_stem are None, the path's
	stem is returned. This function does not change the given path. Use
	make_altered_name instead to append an extension.

	Args:
		path (pathlib.Path): the file path that provides the original stem
		before_stem (str): the string to add to the beginning of the path's
			stem. If it is None, nothing is added to the stem's beginning.
			Defaults to None.
		after_stem (str): the string to add to the end of the path's stem. If
			it is None, nothing is added to the stem's end. Defaults to None.

	Returns:
		str: a new file stem with the specified additions
	"""
	stem = get_file_stem(path)

	if before_stem is not None:
		stem = before_stem + stem

	if after_stem is not None:
		stem += after_stem

	return stem
