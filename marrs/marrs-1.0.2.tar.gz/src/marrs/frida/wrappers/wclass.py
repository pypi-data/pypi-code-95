"""
A wrapper class - represents a Java class.
"""


class Class:

	def __init__(self, class_data, agent):
		self.agent = agent

		self.name = class_data['name']

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return "Class('{0}')".format(self.name)

	def get_methods(self, is_static=None, name_substr=None):
		return self.agent.get_methods(self.name, is_static=is_static, name_substr=name_substr)

	def get_fields(self, is_static=None, name_substr=None):
		return self.agent.get_fields(self.name, is_static=is_static, name_substr=name_substr)

	def get_constructors(self):
		return self.agent.get_constructors(self.name)

	def get_instances(self):
		return self.agent.get_instances(self.name)

	def set_field(self, field_name, value):
		self.agent.set_static_field_value(self.name, field_name, value)

	def get_field(self, field_name):
		return self.agent.get_static_field_value(self.name, field_name)

	def new(self, params=[], param_types=None):
		return self.agent.new_instance(self.name, params, param_types)
