"""
A wrapper class - represents a Java instance.
"""


class Instance:

	def __init__(self, instance_data, agent):
		self.class_name = instance_data.get('class_name')
		self.id = instance_data['id']

		self.agent = agent

	def __repr__(self):
		class_str = "class='{0}', ".format(self.class_name) if self.class_name else ''
		return "Instance({0}toString='{1}')".format(class_str, self.__str__())

	def __str__(self):
		return self.agent.__to_string__(self.id)

	def get_fields(self, name_substr=None):
		return self.agent.get_fields(self.class_name, is_static=False, name_substr=name_substr)

	def get(self, field_name):
		return self.agent.__get_field_value__(self.class_name, field_name, instance_id=self.id)

	def call(self, method_name, params=[], param_types=[]):
		return self.agent.__call_instance_method__(self.id, method_name, params, param_types)

	def to_string(self):
		return self.agent.__to_string__(self.id)
