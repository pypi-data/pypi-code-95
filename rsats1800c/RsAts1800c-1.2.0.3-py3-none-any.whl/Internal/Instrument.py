import re
from typing import List
import pyvisa
from . import Utilities, Conversions
from .Utilities import trim_str_response
from . import InstrumentErrors


class Instrument(object):
	"""Model of an Instrument with VISA interface."""

	def __init__(self, resource_name: str):
		"""Opening an instrument session."""
		self.resource_name = resource_name

		# open VISA session
		self._rm = pyvisa.ResourceManager()
		self._session = self._rm.open_resource(resource_name)
		self._session.write_termination = '\0'
		self._session.set_visa_attribute(pyvisa.constants.VI_ATTR_TERMCHAR, 0)
		self._session.set_visa_attribute(pyvisa.constants.VI_ATTR_TERMCHAR_EN, True)
		self._session.set_visa_attribute(pyvisa.constants.VI_ATTR_TMO_VALUE, 5000)
		self.idn_string = Utilities.trim_str_response(self.query_str('*IDN?')).strip()

	def __str__(self):
		return f"Instrument Model: '{self.model}', ResourceName: '{self.resource_name}'"

	@property
	def visa_manufacturer(self) -> str:
		"""Returns the visa manufacturer of the current session."""
		return self._session.manufacturer

	@property
	def idn_string(self) -> str:
		return self._idn_string

	@idn_string.setter
	def idn_string(self, value: str) -> None:
		"""IDN string. Set it to force a different IDN string than the default *IDN? response."""
		self._idn_string = value
		self._parse_idn_string(self._idn_string)

	@property
	def visa_timeout(self) -> int:
		"""See the visa_timeout.setter."""
		return self._session.visa_timeout

	@visa_timeout.setter
	def visa_timeout(self, value: int) -> None:
		"""Sets / Gets visa IO timeout in milliseconds."""
		self._session.visa_timeout = value

	def _parse_idn_string(self, idn_string: str) -> None:
		"""Parse the *IDN? response to:
		- Manufacturer
		- Model
		- SerialNumber
		- FirmwareRevision"""
		idn_string = idn_string.strip()
		m = re.search(r'([\w& ]+),([a-zA-Z ]+)([\-0-9a-zA-Z ]*),([^,]+),([\w .\-/]+)', idn_string)
		if not m:
			raise Exception(f"The instrument *IDN? string parsing failed. Parsed *IDN? response: '{idn_string}'")
		self.manufacturer = m.group(1).strip()
		self.model = m.group(2).strip()
		self.full_model_name = self.model + m.group(3).strip()
		self.serial_number = m.group(4).strip()
		self.firmware_version = m.group(5).strip()

	def fits_idn_pattern(self, patterns: List[str], supported_models: List[str]) -> None:
		"""Throws exception if the current instrument model does not fit  any of the patterns.
		The supported_models argument is only used for exception messages"""
		matches = False
		assert self._idn_string, f'*IDN? was not assigned yet.'
		for x in patterns:
			matches = re.search(x, self.model)
			if matches is True:
				break
		if not matches:
			raise Exception(f"Instrument *IDN? query model '{self.model}' is not supported. Supported models: {', '.join(supported_models)}")

	@staticmethod
	def _parse_err_query_response(response: str) -> str:
		"""Parses entered response string to string error message without the error code.
		E.g.: response = '-110,"Command error"' returns: 'Command error'."""
		m = re.match(r'(-?[\d]+).*"(.*)"', response)
		if m:
			return m.group(2)
		else:
			return response

	def reset(self) -> None:
		"""Resets the instrument and clears its status."""
		self.write("*RST")

	def preset(self) -> None:
		"""Presets the instrument to the default settings."""
		self.write("SYST:PRES")

	def _write_read(self, cmd: str) -> str:
		"""Writes the command and reads the response.
		For writes the response is the error code. 0 means success."""
		self._session.write(cmd)
		response = self._session.read(encoding='charmap')
		if response.endswith('\0'):
			response = response.strip('\0')
		response = response.strip()
		if "Unknown Command:" in response:
			raise InstrumentErrors.StatusException(self.resource_name, f'Error by command "{cmd}", error: {response}')
		return response

	def write(self, cmd: str) -> None:
		"""Writes string command to the instrument."""
		response = self._write_read(cmd)
		code = Conversions.str_to_int(response)
		if code == -999:
			raise InstrumentErrors.StatusException(self.resource_name, f'Execution error by command "{cmd}"')
		elif code == -997:
			raise InstrumentErrors.StatusException(self.resource_name, f'Argument out of range by command "{cmd}"')

	def write_bool_as_int(self, cmd: str, param: bool) -> None:
		"""Writes the string command with the boolean parameter formatted as 0 or 1. Boolean parameter has leading space."""
		param_cmd = ' 1' if param is True else ' 0'
		self.write(cmd + param_cmd)

	def write_int(self, cmd: str, param: int) -> None:
		"""Writes the string command followed by a space and the integer parameter formatted."""
		self.write(cmd + f' {param}')

	def write_float(self, cmd: str, param: float) -> None:
		"""Writes the string command followed by a space and the float parameter formatted for 2 decimal places."""
		param_cmd = f' {format(param, ".2f")}'
		self.write(cmd + param_cmd)

	def query_str(self, query: str) -> str:
		"""Sends a query and reads response from the instrument.
		The response is trimmed of any trailing LF and \0 characters and has no length limit."""
		return self._write_read(query)

	def query_int(self, query: str) -> int:
		"""Sends a query and reads response from the instrument as integer."""
		string = self.query_str(query)
		return Conversions.str_to_int(string)

	def query_float(self, query: str) -> float:
		"""Sends a query and reads response from the instrument as float number."""
		string = self.query_str(query)
		return Conversions.str_to_float(string)

	def query_bool(self, query: str) -> bool:
		"""Sends a query and reads response from the instrument as boolean value."""
		string = self.query_str(query)
		return Conversions.str_to_bool(string)

	def query_str_list(self, query: str) -> List[str]:
		"""Sends a query and reads response from the instrument as csv-list."""
		response = self.query_str(query).split(',')
		response = [trim_str_response(x) for x in response]
		return response

	def close(self) -> None:
		"""Closes the Instrument session."""
		self._session.close()
		self._session = None
