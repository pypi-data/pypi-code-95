from pathlib import Path
from .path_util import get_file_stem
from .extension_possessor import ExtensionPossessor


_TYPES_PATH_STR = (Path, str)


class PathChecker(ExtensionPossessor):
	"""
	This class contains a pathlib.Path object (property path) and a tuple of
	suffixes (property extension) that make the extension the path is supposed
	to have. PathChecker can verify whether the path has the right extension,
	whether it exists and whether it is a directory or a file.

	In this class, a file's stem is defined as its name without the extension.
	In Pathlib, however, the stem is the file name without the last suffix.
	"""

	def __init__(self, a_path, suffixes):
		"""
		The constructor needs a file path and a list or tuple of suffixes that
		make the expected extension. If a_path is a string, it will be
		converted to a pathlib.Path object. If it is of type pathlib.Path, a
		copy of it will be kept. See the documentation of superclass
		ExtensionPossessor for a description of valid extensions.

		Args:
			a_path (pathlib.Path or str): the path that this instance will
				check.
			suffixes (list or tuple): the extension that the path is supposed
				to have. If None, the extension will be an empty tuple.

		Raises:
			TypeError: if a_path is not an instance of str or pathlib.Path or
				if suffixes is not None, nor a list or a tuple
		"""
		ExtensionPossessor.__init__(self, suffixes)
		self._set_path(a_path)

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

		return self._path == other._path and self.extension == other.extension

	def __repr__(self):
		return self.__class__.__name__ + "('" + str(self._path) + "', "\
			+ str(self.extension) + ")"

	def extension_is_correct(self):
		"""
		Indicates whether path's extension matches the expected extension.

		Returns:
			bool: True if path has the right extension, False otherwise
		"""
		# pathlib.Path objects store their extension in a list.
		return tuple(self._path.suffixes) == self.extension

	def get_file_name(self):
		"""
		Provides the name of the file that path points to.

		Returns:
			str: the name of the file that path points to
		"""
		return self._path.name

	def get_file_stem(self):
		"""
		Provides the stem of the file that path points to.

		Returns:
			str: the stem of the file that path points to
		"""
		return get_file_stem(self._path)

	@property
	def path(self):
		"""
		This read-only property returns a copy of the path that this object
		checks. It is an instance of pathlib.Path.
		"""
		return Path(self._path)

	def path_exists(self):
		"""
		Indicates whether path points to an existent directory or file.

		Returns:
			bool: True if path exists, False otherwise
		"""
		return self._path.exists()

	def path_is_dir(self):
		"""
		Indicates whether path points to a directory.

		Returns:
			bool: True if path exists and is a directory, False otherwise
		"""
		return self._path.is_dir()

	def path_is_file(self):
		"""
		Indicates whether path points to a file.

		Returns:
			bool: True if path exists and is a file, False otherwise
		"""
		return self._path.is_file()

	def _set_path(self, a_path):
		"""
		Sets the path checked by this object. If a_path is a string, it will
		be converted to a pathlib.Path object. If it is of type pathlib.Path,
		a copy of it will be kept.

		Args:
			a_path (pathlib.Path or str): the path that this object must check

		Raises:
			TypeError: if a_path is not an instance of pathlib.Path or str
		"""
		if isinstance(a_path, _TYPES_PATH_STR):
			self._path = Path(a_path)

		else:
			raise TypeError(
				"The given path must be an instance of pathlib.Path or str.")
