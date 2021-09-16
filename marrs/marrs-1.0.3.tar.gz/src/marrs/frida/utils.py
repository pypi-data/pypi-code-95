import re

from ..utils import invert_dict

JAVA_PRIMITIVE_TYPE_TO_WRAPPER_CLASS_MAPPING = {
	'int': 'java.lang.Integer',
	'boolean': 'java.lang.Boolean',
	'char': 'java.lang.Character',
	'float': 'java.lang.Float',
	'double': 'java.lang.Double',
	'byte': 'java.lang.Byte',
	'short': 'java.lang.Short',
	'long': 'java.lang.Long',
}

JAVA_PRIMITIVE_TYPES = JAVA_PRIMITIVE_TYPE_TO_WRAPPER_CLASS_MAPPING.keys()

JAVA_PRIMITIVE_TYPE_TO_ARRAY_LETTER_MAPPING = {
	'byte': 'B',
	'short': 'S',
	'int': 'I',
	'long': 'J',
	'float': 'F',
	'double': 'D',
	'boolean': 'Z',
	'char': 'C',
}

JAVA_CLASS_TYPE_ARRAY_LETTER = 'L'

ARRAY_LETTER_TO_JAVA_PRIMITIVE_TYPE_MAPPING = invert_dict(JAVA_PRIMITIVE_TYPE_TO_ARRAY_LETTER_MAPPING)


def is_java_primitive_type(class_name):
	return class_name in JAVA_PRIMITIVE_TYPES


def primitive_type_to_letter(class_name):
	return JAVA_PRIMITIVE_TYPE_TO_ARRAY_LETTER_MAPPING.get(class_name, class_name)


def is_simple_array_type(class_name):
	return class_name and class_name.endswith('[]')


def is_java_array_type(class_name):
	return class_name and class_name.startswith('[')


def java_primitive_type_to_wrapper_class(prim_type):
	return JAVA_PRIMITIVE_TYPE_TO_WRAPPER_CLASS_MAPPING.get(prim_type, prim_type)


def is_java_class_type(class_name):
	return class_name is not None and not is_java_primitive_type(class_name) and not is_simple_array_type(
		class_name) and not is_java_array_type(
		class_name)


def convert_to_api_class_name(class_name):
	# for now only deal with converting simple array name
	if is_simple_array_type(class_name):
		groups = re.search(r"(.+?)((?:\[\])+)", class_name).groups()
		elem_type = groups[0]
		brackets = groups[1]

		prefix = '[' * (len(brackets) // 2)
		if is_java_primitive_type(elem_type):
			letter = primitive_type_to_letter(elem_type)
			return prefix + letter

		# class type
		return prefix + JAVA_CLASS_TYPE_ARRAY_LETTER + elem_type + ';'

	return class_name


def get_java_array_type(elem_type, depth):
	prefix = ('[' * (depth - 1))
	if is_java_primitive_type(elem_type):
		return prefix + JAVA_PRIMITIVE_TYPE_TO_ARRAY_LETTER_MAPPING[elem_type]

	return prefix + JAVA_CLASS_TYPE_ARRAY_LETTER + elem_type + ";"


def simplify_java_array_type(class_name):
	if not is_java_array_type(class_name):
		return class_name

	groups = re.search(r"(\[+)(\w)(.*)", class_name).groups()
	dimensions = len(groups[0])
	letter = groups[1]

	if letter == JAVA_CLASS_TYPE_ARRAY_LETTER:  # class type
		arr_type = groups[2][:-1]
	else:
		arr_type = ARRAY_LETTER_TO_JAVA_PRIMITIVE_TYPE_MAPPING[letter]

	return arr_type + ('[]' * dimensions)


def extract_elem_type_from_simple_arr_type(class_name):
	if not is_simple_array_type(class_name):
		return class_name

	return class_name[:-2]


def extract_base_elem_type_from_simple_arr_type(class_name):
	if not is_simple_array_type(class_name):
		return class_name

	groups = re.search(r"(.+?)((?:\[\])+)", class_name).groups()
	arr_type = groups[0]
	return arr_type
