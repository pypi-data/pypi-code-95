import math
import sys
from enum import Enum
from typing import List
from . import Utilities


class BinFloatFormat(Enum):
	"""Binary format of a float number."""
	Single_4bytes = 1
	Single_4bytes_swapped = 2
	Double_8bytes = 3
	Double_8bytes_swapped = 4


class BinIntFormat(Enum):
	"""Binary format of an integer number."""
	Integer32_4bytes = 1
	Integer32_4bytes_swapped = 2
	Integer16_2bytes = 3
	Integer16_2bytes_swapped = 4


def assert_string_data(value: str) -> None:
	"""Asserts value is string type."""
	assert isinstance(value, str), f"Input value type must be string. Actual type: {type(value)}, value: {value}"


def assert_list_data(value: list) -> None:
	"""Asserts value is list type."""
	assert isinstance(value, list), f"Input value type must be a list. Actual type: {type(value)}, value: {value}"


bool_true_lookup = frozenset(['1', 'on', 'On', 'ON', 'true', 'True', 'TRUE'])
bool_false_lookup = frozenset(['0', 'off', 'Off', 'OFF', 'false', 'False', 'FALSE'])


def str_to_bool(string: str) -> bool:
	"""Converts string to boolean value.
	The function robust, and case insensitive.
	If the string can not be converted to a boolean, the function returns False."""
	assert_string_data(string)
	if string in bool_true_lookup:
		return True
	if string in bool_false_lookup:
		return False
	string = string.strip()
	if string in bool_true_lookup:
		return True
	if string in bool_false_lookup:
		return False
	string = Utilities.trim_str_response(string)
	if string in bool_true_lookup:
		return True
	if string in bool_false_lookup:
		return False
	return False


number_plus_inf_lookup = frozenset(['Inf', 'INF', 'INFINITY', '+Inf', '+INF', '+inf', '+INFINITY', '+Infinity', '+infinity'])
number_minus_inf_lookup = frozenset(['-Inf', '-INF', '-inf', '-INFINITY', '-Infinity', '-infinity'])
number_nan_lookup = frozenset(['Nan', 'NAN', 'nan', 'NaN', 'NAV', 'NaV', 'NCAP', 'INV', 'NONE', 'none', 'None', 'DTX'])
number_max_lookup = frozenset(['OFL', 'ofl', 'Ofl'])
number_min_lookup = frozenset(['UFL', 'ufl', 'Ufl'])
int_neg_inf = -(sys.maxsize - 1)


def str_to_int(string: str) -> int:
	"""Converts string to integer value. Float values are coerced to integer.
	Also recognizes case insensitive special values like NaN, INV, NCAP..."""
	assert_string_data(string)
	string = string.strip()
	if string == '':
		return 0
	value = str_special_values_to_int(string)
	if value:
		return value

	# Hexadecimal numbers
	if string.startswith('#H') or string.startswith('0x'):
		if ',' in string:
			return int(string[2:string.find(',')], 16)
		else:
			return int(string[2:], 16)

	# Binary numbers
	if string.startswith('#B') or string.startswith('0b'):
		if ',' in string:
			return int(string[2:string.find(',')], 2)
		else:
			return int(string[2:], 2)

	# Octal numbers
	if string.startswith('#Q') or string.startswith('0o'):
		if ',' in string:
			return int(string[2:string.find(',')], 8)
		else:
			return int(string[2:], 8)

	return int(round(float(string)))


def str_special_values_to_int(string: str) -> int:
	"""Converts special string values to integer. Returns None if no special value was found."""
	assert_string_data(string)
	if string in number_plus_inf_lookup or string in number_max_lookup:
		return sys.maxsize
	if string in number_minus_inf_lookup or string in number_min_lookup or string in number_nan_lookup:
		return int_neg_inf
	if string == 'OFF':
		return int_neg_inf + 1
	if string == 'OK':
		return sys.maxsize - 1
	if string == 'DC':
		# noinspection PyTypeChecker
		return int_neg_inf / 100
	if string == 'ULEU':
		return int(sys.maxsize / 10)
	if string == 'ULEL':
		# noinspection PyTypeChecker
		return int_neg_inf / 10
	# noinspection PyTypeChecker
	return None


def str_to_float(string: str) -> float:
	"""Converts string to float value.
	Also recognizes case insensitive special values like NaN, INV, NCAP..."""
	assert_string_data(string)
	string = string.strip()
	if string == '':
		return 0.0
	if string in number_plus_inf_lookup:
		return math.inf
	if string in number_minus_inf_lookup:
		return -math.inf
	if string in number_nan_lookup:
		return math.nan
	if string in number_max_lookup:
		return sys.float_info.max
	if string in number_min_lookup:
		return -sys.float_info.max
	if string == 'OFF':
		return -sys.float_info.epsilon
	if string == 'OK':
		return sys.float_info.epsilon
	if string == 'DC' or string == '':
		return -sys.float_info.max / 100
	if string == 'ULEU':
		return sys.float_info.max / 10
	if string == 'ULEL':
		return -sys.float_info.max / 10
	return float(string)


def float_to_str(value: float) -> str:
	"""Converts double number to string using {.12g} formatter."""
	return format(value, ".12g")


def bool_to_str(value: bool) -> str:
	"""Converts boolean to 'ON' or 'OFF' string."""
	if type(value) is bool:
		return 'ON' if value is True else 'OFF'
	else:
		raise Exception(f"bool_to_str: unsupported variable type '{type(value)}', value '{value}'. Only boolean values are supported.")


def str_enclose_by_quotes(string: str) -> str:
	"""Returns string enclosed by single quotes."""
	assert_string_data(string)
	return "'" + string + "'"


def list_to_csv_str(value: list) -> str:
	"""Converts list of elements to strings separated by commas.
	Element types can differ on an individual basis.
	Supported element types:
	- int
	- bool
	- float
	- string -> string no quotes
	- enum"""
	assert_list_data(value)
	result = []
	for x in value:
		el = value_to_str(x)
		if not el:
			raise TypeError(f"List element type is not supported by Conversions.list_to_csv_str: '{x}'")
		result.append(el)
	return ','.join(result)


def list_to_csv_quoted_str(value: list) -> str:
	"""Converts list of elements to quoted strings separated by commas.
	Only string elements are enclosed by single quotes
	Element types can differ on an individual basis.
	Supported element types:
	- int
	- bool
	- float
	- string -> string enclosed by quotes
	- enum"""
	assert_list_data(value)
	result = []
	for x in value:
		if isinstance(x, str):
			el = str_enclose_by_quotes(x)
		else:
			el = value_to_str(x)
		if not el:
			raise TypeError(f"List element type is not supported by Conversions.list_to_csv_quoted_str: '{x}'")
		result.append(el)

	return ','.join(result)


def decimal_value_to_str(x: int or float) -> str:
	"""Converts scalar decimal value to string.
		Supported element types:
			- int
			- float"""

	if isinstance(x, int) and type(x) is not bool:
		return str(x)
	elif isinstance(x, float):
		return float_to_str(x)
	else:
		raise Exception(f"decimal_value_to_str: unsupported variable type '{type(x)}', value '{x}'. Only integer and float types are supported.")


def value_to_str(x: int or bool or float or str or Enum) -> str:
	"""Converts scalar value to string.
	Supported element types:
		- int
		- bool
		- float
		- string
		- enum"""
	if isinstance(x, bool):
		return bool_to_str(x)
	elif isinstance(x, int):
		return str(x)
	elif isinstance(x, float):
		return float_to_str(x)
	elif isinstance(x, str):
		return x
	elif isinstance(x, Enum):
		return x.name.lstrip('_')
	else:
		raise Exception(f"value_to_str: unsupported variable type '{type(x)}', value '{x}'. Supported types: int, bool, float, str, enum.")


def value_to_quoted_str(x: int or bool or float or str or Enum) -> str:
	"""Converts scalar value to string enclosed by single quotes.
	Supported element types:
		- int
		- bool
		- float
		- string
		- enum"""
	return f"'{value_to_str(x)}'"


def str_to_float_list(string: str) -> List[float]:
	"""Converts string with comma-separated values to list of Floats."""
	assert_string_data(string)
	if not string:
		return []

	result = [*map(str_to_float, string.split(','))]
	return result


def str_to_int_list(string: str) -> List[int]:
	"""Converts string with comma-separated values to list of Integers."""
	assert_string_data(string)
	if not string:
		return []

	result = [*map(str_to_int, string.split(','))]
	return result


def str_to_bool_list(string: str) -> List[bool]:
	"""Converts string with comma-separated values to list of booleans."""
	assert_string_data(string)
	if not string:
		return []

	result = [*map(str_to_bool, string.split(','))]
	return result


def str_to_str_list(string: str) -> List[str]:
	"""Converts string with comma-separated values to list of strings.
	Each element is trimmed by trim_str_response()"""
	assert_string_data(string)
	if not string:
		return []

	result = [*map(Utilities.trim_str_response, string.split(','))]
	return result


def find_in_enum_members(item, enum_members: list):
	"""Matches a string in the provided list of member strings.
	The item must be not fully matched.
	Rules:
	- If the member string starts with underscore, it is cut out before the matching continues.
	- The item is matched if a member string starts with the item (item is a prefix of the member)."""
	found = None
	for x in enum_members:
		if x.startswith(item):
			found = x
			break
		if x.startswith('_'):
			# Trim underscore if exists, this is used to escape the first Enum character being a number - not accepted by Python or C#
			if x.strip('_').startswith(item):
				found = x
				break
	return found


def str_to_scalar_enum_helper(string: str, enum_type: Enum, enum_members=None) -> Enum:
	"""Converts string to one enum element.
	enum_members are optional to improve the performance for repeated conversions.
	If you do not provide them, they are generated inside the function."""
	value = Utilities.trim_str_response(string)
	if not enum_members:
		# noinspection PyTypeChecker
		enum_members = [x.name for x in enum_type]
	found = find_in_enum_members(value, enum_members)
	if found:
		return enum_type[found]
	# If not found, search in the special integer numbers:
	spec_value = str_special_values_to_int(value)
	if not spec_value:
		raise Exception(f"String '{value}' can not be found in the enum type '{enum_type}'")
	# noinspection PyTypeChecker
	return spec_value


def str_to_list_enum_helper(string: str, enum_type: Enum, enum_members=None) -> List[Enum]:
	"""Converts string to list of enum elements.
	enum_members are optional to improve the performance for repeated conversions.
	If you do not provide them, they are generated inside the function."""
	if not enum_members:
		# noinspection PyTypeChecker
		enum_members = [x.name for x in enum_type]
	elements = string.split(',')
	return [str_to_scalar_enum_helper(x, enum_type, enum_members) for x in elements]


def enum_scalar_to_str(data, enum_type) -> str:
	"""Converts enum scalar value to string."""
	assert isinstance(data, enum_type), f"Expected command parameter {enum_type}, actual data type: {type(data)}. Value: {data}"
	return value_to_str(data)


def enum_list_to_str(data: List, enum_type) -> str:
	"""Converts enum list to csv-string."""
	# For enums, check that each element is an enum
	assert all(isinstance(x, enum_type) for x in data), f"Expected command parameter list of {enum_type}, detected one or more elements of non-enum type. Value: {data}"
	return list_to_csv_str(data)


def str_to_scalar_enum(string: str, enum_type) -> Enum:
	"""Converts string to one enum element."""
	return str_to_scalar_enum_helper(string, enum_type)


def str_to_list_enum(string: str, enum_type) -> List[Enum]:
	"""Converts string to list of enum elements."""
	return str_to_list_enum_helper(string, enum_type)
