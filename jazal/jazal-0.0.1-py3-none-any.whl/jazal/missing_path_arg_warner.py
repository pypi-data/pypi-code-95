from .extension_possessor import ExtensionPossessor
from .path_checker import PathChecker
from .reactive_path_checker import ReactivePathChecker


class MissingPathArgWarner(ExtensionPossessor):
	"""
	This class' main purpose is to warn the programmer that a path was not
	provided to a function or a script as an argument. If a path is given, the
	class allows to instantiate PathChecker or ReactivePathChecker. This class
	needs the name of the argument that the path is the value of
	(property arg_name) and the extension that the path is supposed to have
	(property extension).
	"""

	def __init__(self, arg_name, suffixes):
		"""
		The constructor requires a path argument name and a list or tuple
		containing the suffixes that make the file extension expected from the
		path. The suffixes must conform to the documentation of superclass
		ExtensionPossessor.

		Args:
			arg_name (str): the name of a path argument
			suffixes (list or tuple): the extension expected from the path
				argument

		Raises:
			TypeError: if argument suffixes is not None, nor a list or a tuple
		"""
		ExtensionPossessor.__init__(self, suffixes)
		self._arg_name = arg_name

	@property
	def arg_name(self):
		"""
		This read-only property is the name of the path argument that may be
		missing.
		"""
		return self._arg_name

	def make_missing_arg_msg(self):
		"""
		The message created by this method tells that the argument named
		<argument name>, the path to a file with extension
		<expected extension>, is needed. It is relevant if the argument is
		missing.

		Returns:
			str: a message telling that the argument is needed
		"""
		return self._arg_name + ": the path to a file with extension '"\
			+ self.extension_to_str() + "' must be provided."

	def make_path_checker(self, path):
		"""
		Creates a PathChecker instance with property extension and the given
		file path.

		Args:
			path (pathlib.Path or str): It should be the value of the
				path argument associated with this object.

		Returns:
			PathChecker: an object able to verify the path argument's value
		"""
		return PathChecker(path, self.extension)

	def make_reactive_path_checker(self, path):
		"""
		Creates a ReactivePathChecker instance with properties extension and
		arg_name and the given file path.

		Args:
			path (pathlib.Path or str): It should be the value of the
				path argument associated with this object.

		Returns:
			ReactivePathChecker: an object able to verify the path argument's value
		"""
		return ReactivePathChecker(path, self.extension, self.arg_name)
