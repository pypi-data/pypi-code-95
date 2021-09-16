"""
A wrapper class - represents a Java field.
"""


class Field:

	def __init__(self, field_data, agent):
		self.class_name = field_data['class_name']
		self.name = field_data['name']
		self.declaration = field_data['declaration']
		self.type = field_data['type']
		self.is_static = field_data['is_static']

		self.agent = agent

	def __repr__(self):
		return "[{static}Field(Name={name}, Type={type})]".format(
			name=self.name,
			type=self.type,
			static="Static " if self.is_static else '')

	def __str__(self):
		return self.__repr__()
