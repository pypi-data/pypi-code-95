"""
A wrapper class - represents a Java method.
"""


class Method:

	def __init__(self, method_data, agent):
		self.class_name = method_data['class_name']
		self.name = method_data['name']
		self.signature = method_data['signature']
		self.is_static = method_data['is_static']
		self.return_type = method_data['return_type']
		self.param_types = method_data['param_types']

		self._agent = agent

	def __repr__(self):
		params_str = '' if self.param_types == [] else ', ParamTypes={param_types}'.format(param_types=self.param_types)
		return "[{static}Method(Name={name}, ReturnType={return_type}{params_str})]".format(
			name=self.name,
			static="Static " if self.is_static else '',
			return_type=self.return_type,
			params_str=params_str)

	def __str__(self):
		return self.__repr__()
