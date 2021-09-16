"""
A wrapper class - represents a Java class constructor.
"""


class Constructor:

	def __init__(self, constructor_data, agent):
		self.class_name = constructor_data['class_name']
		self.signature = constructor_data['signature']
		self.param_types = constructor_data['param_types']

		self.agent = agent

	def __repr__(self):
		params_str = '' if self.param_types == [] else ', ParamTypes={param_types}'.format(param_types=self.param_types)
		return "[Constructor(Class={class_name}{params_str})]".format(
			class_name=self.class_name,
			params_str=params_str)

	def __str__(self):
		return self.__repr__()

	def new(self, params=[]):
		return self.agent.new_instance(self.class_name, params, self.param_types)
