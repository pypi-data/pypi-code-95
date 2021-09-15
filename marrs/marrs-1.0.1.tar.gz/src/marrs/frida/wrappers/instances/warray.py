"""
A wrapper class - represents a Java array.
"""

from .winstance import Instance
from ...utils import simplify_java_array_type, extract_elem_type_from_simple_arr_type


class ArrayIterator:
	def __init__(self, arr):
		self._arr = arr
		self._index = 0

	def __next__(self):
		if self._index < len(self._arr):
			res = self._arr[self._index]
			self._index += 1
			return res

		raise StopIteration


class Array(Instance):

	def __init__(self, array_data, agent):
		array_data['class_name'] = simplify_java_array_type(array_data.get('class_name'))

		super().__init__(array_data, agent)

		self.elem_type = None
		if self.class_name:
			self.elem_type = extract_elem_type_from_simple_arr_type(self.class_name)

		# calculate length of array
		self.size = self.length()

	def __iter__(self):
		return ArrayIterator(self)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		s = '['
		for i in range(self.size):
			item = self[i]
			s += str(item)
			if i < self.size - 1:
				s += ', '
		s += ']'
		return s

	def _validate_index(self, index):
		if self.size == 0:
			raise IndexError("Array size is 0")
		if index < 0 or index >= self.size:
			raise IndexError("Index is out of range [0, {0}]".format(self.size - 1))

	def __getitem__(self, index):
		self._validate_index(index)

		value_data = self.agent.api.array_get_item(self.id, index)
		return self.agent._value_data_to_python_value(value_data)

	def __setitem__(self, index, value):
		self._validate_index(index)

		value_to_set = self.agent._convert_to_api_js_value(value)

		self.agent.api.array_set_item(self.id, index, value_to_set)

	def __len__(self):
		return self.size

	def length(self):
		return self.agent.api.get_array_length(self.id)

	def to_list(self):
		return [x for x in self]
