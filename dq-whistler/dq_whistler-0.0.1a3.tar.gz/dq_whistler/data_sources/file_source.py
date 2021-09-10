from typing import Optional, Dict
from dq_whistler.data_sources.data_source import DataSource


class FileSourceOptions:
	"""
	Base class of options for file based source
	Args:
		path (str): path of the file
		delimiter (str, optional): separator between two fields
		header (str, optional): header row is present in the file or not
		infer_schema (str, optional): to infer schema by default while reading the file
		file_format (str): the format of the file i.e csv, avro, parquet etc

	Returns:

	Raises:

	Examples:
		A really great idea.  A way you might use me is
		>>> print FileSourceOptions(path='foo', format="csv", delimiter=",", header="true", infer_schema="true")
		BTW, this always returns 0.  **NEVER** use with :class:`MyPublicClass`.
	"""

	_path: str
	_file_format: str
	_delimiter: str
	_header: str
	_infer_schema: str

	def __init__(
			self,
			path: str,
			file_format: str,
			delimiter: Optional[str] = ",",
			header: Optional[str] = "true",
			infer_schema: Optional[str] = "true",
	) -> object:
		self._path = path
		self._file_format = file_format
		self._delimiter = delimiter
		self._header = header
		self._infer_schema = infer_schema

	@property
	def get_path(self):
		"""str: Returns the path of the file"""
		return self._path

	@property
	def get_file_format(self):
		"""str: Returns the format of the file"""
		return self._file_format

	@property
	def get_delimiter(self):
		"""str: Returns the delimiter of the file"""
		return self._delimiter

	@property
	def get_header(self):
		"""bool: Returns whether the header read flag is enabled or not"""
		return bool(self._header)

	@property
	def get_infer_schema(self):
		"""bool: Returns whether the infer schema flag is enabled or not"""
		return bool(self._infer_schema)


class FileSource(DataSource):
	"""
	Base class for file based source
	Args:
		path (str): path of the file
		delimiter (str, optional): separator between two fields
		header (str, optional): header row is present in the file or not
		infer_schema (str, optional): to infer schema by default while reading the file
		file_format (str): the format of the file i.e csv, avro, parquet etc

	Returns:

	Raises:

	Examples:
		A really great idea.  A way you might use me is
		>>> print FileSourceOptions(path='foo', format="csv", delimiter=",", header="true", infer_schema="true")
		BTW, this always returns 0.  **NEVER** use with :class:`MyPublicClass`.
	"""

	def __init__(
			self,
			path: str,
			file_format: str,
			delimiter: Optional[str] = ",",
			header: Optional[str] = "true",
			infer_schema: Optional[str] = "true",
			quality_config: Optional[Dict[str, str]] = None,
	):
		super().__init__(
			quality_config
		)
		self._file_source_options = FileSourceOptions(
			path=path, file_format=file_format, delimiter=delimiter, header=header, infer_schema=infer_schema
		)

	def validate(self):
		"""validates the quality resources"""
		raise NotImplementedError

	def read(self):
		pass

	def run_quality_checks(self):
		pass

	@property
	def get_source_options(self):
		"""FileSourceOptions: Returns the object containing options for this source"""
		return self._file_source_options
