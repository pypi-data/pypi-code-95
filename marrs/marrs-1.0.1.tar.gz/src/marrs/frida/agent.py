"""
A Pythonic API (or wrapper) for `frida`'s-like operations on an Android app.
This object is attached to a specific app on a specific device.
It lets you hook and call methods, change field's value, and more.
Can be retrieved by calling :py:meth:`~marrs.app.App.attach_frida_agent` method on an :py:class:`~marrs.app.App` object.
"""

import json
import os

import frida

from .hooks.hooks_manager import HooksManager
from .output_window_client import OutputWindowClient
from .utils import is_simple_array_type, \
	convert_to_api_class_name, java_primitive_type_to_wrapper_class, is_java_class_type, \
	extract_base_elem_type_from_simple_arr_type
from .wrappers import Field, Method, Constructor, Class
from .wrappers.instance_factory import InstanceFactory
from .wrappers.instances import Instance
from ..utils import get_dir_path, read_file


class FridaAgent:

	def __init__(self, app, initial_script=None):
		self.app = app
		self.output = OutputWindowClient(device_id=app.device.id, app_name=app.name)
		self.hooks = HooksManager(self)

		self.app.device.__log__(
			"Creating new frida agent for app", extra_info=app.name)

		if initial_script:
			self.app.device.__warn__(
				"	Initial script is not empty and app is running so restarting app")
			app.force_stop()
			device = frida.get_device(self.app.device.id, timeout=1)
			self.app.device.__log__("	Spawning app", extra_info=self.app.name)
			pid = device.spawn([self.app.name])
			self.app.device.__log__(
				"	Attaching to app", extra_info="pid={pid}".format(pid=pid))
			self.session = device.attach(pid)

			self.__load_api__()
			self.load_script(initial_script)

			device.resume(pid)
			return

		if not app.is_running():
			self.app.device.__log__("	App is not running, starting app")
			app.start()

		self.session = frida.get_device(
			self.app.device.id, timeout=1).attach(self.app.name)
		self.__load_api__()

	def __del__(self):
		self.kill()

	def __print__(self, s):
		if self.output.started:
			self.output.print(s)
		else:
			print(s)

	def __load_api__(self):
		api_js_path = os.path.join(get_dir_path(__file__), '..', 'data', 'bundle.js')
		self.api_script = self.load_script_from_file(api_js_path)
		self.api = self.api_script.exports

	def __on_message__(self, msg, data):
		# print("__on_message__", msg, data)
		msg_type = msg['type']

		if msg_type == 'send':
			payload = json.loads(msg['payload'])
			payload_type = payload['type']
			if payload_type == 'hook-enter':
				hook_id = payload['hookId']
				hook = self.hooks[hook_id]
				params = payload['params']
				orig_retval = payload['originalRetVal']
				call_num = hook.inc_call_num()

				if hook.show_output:
					self.__print__({
						'type': payload_type,
						'data': {
							'params': params,
							'methodName': hook.method_name,
							'className': hook.class_name,
							'paramTypes': hook.param_types,
							'callNum': call_num
						},
					})

				retval = self.hooks.call(hook_id, params, orig_retval)

				if hook.show_output:
					self.__print__({
						'type': 'hook-leave',
						'data': {
							'params': params,
							'methodName': hook.method_name,
							'className': hook.class_name,
							'paramTypes': hook.param_types,
							'callNum': call_num,
							'retval': retval
						},
					})

				self.api_script.post({
					'type': 'continue@' + str(hook_id),
					'payload': {
						'retval': self._convert_to_api_js_value(retval)
					}
				})

		elif msg_type == 'error':
			self.__print__({
				'type': 'error',
				'data': msg['stack']
			})

	def _get_params_data(self, params, param_types):
		converted_params = [self._convert_to_api_js_value(params[i], param_types[i] if param_types else None) for i in
		                    range(len(params))]

		if param_types is not None:
			param_types = [convert_to_api_class_name(pt) for pt in param_types]

		params_data = json.dumps({
			'params': converted_params,
			'paramTypes': param_types
		})

		return params_data

	def _value_data_to_python_value(self, value_data):
		# check if simple value
		if not isinstance(value_data, dict):
			return value_data

		return InstanceFactory.create(self, value_data)

	def _convert_to_api_js_value(self, python_value, elem_type=None):
		if python_value is None:
			return None

		if isinstance(python_value, list):
			return [self._convert_to_api_js_value(x, elem_type) for x in python_value]

		# If type is class type and value is not an instance, try to create new instance of that type
		if is_java_class_type(elem_type) and not isinstance(python_value, Instance):
			python_value = self.new_instance(elem_type, [str(python_value)])

		if isinstance(python_value, Instance):
			return json.dumps({
				'id': python_value.id,
			})

		return json.dumps({
			'value': python_value
		})

	def load_script_from_file(self, file_path):
		"""
		Load and run a script from file.

		:param file_path: The script's file path
		:type file_path: str
		:return: `frida`'s script object
		"""
		script_code = read_file(file_path)
		return self.load_script(script_code)

	def load_script(self, script_code):
		"""
		Load and run a script.

		:param script_code: The script's code to run
		:type script_code: str
		:return: `frida`'s script object
		"""
		script = self.session.create_script(script_code)
		script.on('message', self.__on_message__)
		script.load()
		return script

	def kill(self):
		"""
		Kills the agent's output window (if exist) and detached from app.
		"""

		# TODO: Unloading all the scripts ?
		self.output.kill()
		self.app.frida_agent = None

	# API methods
	def get_loaded_classes(self, regex_pattern=None):
		"""
		Get a list of loaded classes.

		:param regex_pattern: Match classes' names to this regex pattern
		:type regex_pattern: str
		:return: A list of loaded classes
		:rtype: A list of :py:class:`~marrs.frida.wrappers.wclass.Class`
		"""
		classes = self.api.get_loaded_classes(regex_pattern)
		classes = list(map(lambda c: Class(c, self), classes))
		return classes

	def get_methods(self, class_name, is_static=None, name_substr=None):
		"""
		Get a list of methods of a specific class.

		:param class_name: The full name of the class to get its methods
		:type class_name: str
		:param is_static: Get only static methods. None value (the default) will return both.
		:type is_static: bool
		:param name_substr: Match methods' names that contain this substring
		:type name_substr: str
		:return: A list of methods
		:rtype: A list of :py:class:`~marrs.frida.wrappers.wmethod.Method`
		"""
		class_name = convert_to_api_class_name(class_name)
		methods = self.api.get_methods_of_class(class_name)
		methods = list(map(lambda m: Method(m, self), methods))

		if is_static is not None:
			methods = list(filter(lambda m: m.is_static == is_static, methods))

		if name_substr is not None:
			methods = list(filter(lambda m: name_substr in m.name, methods))

		return methods

	def get_fields(self, class_name, is_static=None, name_substr=None):
		"""
		Get a list of fields of a specific class.

		:param class_name: The full name of the class to get its fields
		:type class_name: str
		:param is_static: Get only static fields. None value (the default) will return both.
		:type is_static: bool
		:param name_substr: Match fields' names that contain this substring
		:type name_substr: str
		:return: A list of fields
		:rtype: A list of :py:class:`~marrs.frida.wrappers.wfield.Field`
		"""
		if class_name is None:
			raise ValueError('class_name is None')

		class_name = convert_to_api_class_name(class_name)
		fields = self.api.get_fields_of_class(class_name)

		fields = list(map(lambda f: Field(f, self), fields))

		if is_static is not None:
			fields = list(filter(lambda f: f.is_static == is_static, fields))

		if name_substr is not None:
			fields = list(filter(lambda f: name_substr in f.name, fields))

		return fields

	def get_instances(self, class_name):
		"""
		Get all the living instances of a given class.

		:param class_name: The full name of the class to get its living instances
		:type class_name: str
		:return: A list of instances
		:rtype: A list of :py:class:`~marrs.frida.wrappers.winstance.Instance`
		"""
		class_name = convert_to_api_class_name(class_name)
		instances_data = self.api.get_instances_of_class(class_name)
		instances_data = list(map(lambda idata: InstanceFactory.create(self, idata), instances_data))
		return instances_data

	def get_class(self, class_name):
		"""
		Get a loaded class by its name.

		:param class_name: The full name of the class
		:type class_name: str
		:return: A class object
		:rtype: :py:class:`~marrs.frida.wrappers.wclass.Class`
		"""
		class_name = convert_to_api_class_name(class_name)
		class_data = self.api.get_class(class_name)
		return Class(class_data, self)

	def get_constructors(self, class_name):
		"""
		Get a list of constructors of a given class.

		:param class_name: The full name of the class
		:type class_name: str
		:return: A list of constructors objects
		:rtype: A list of :py:class:`~marrs.frida.wrappers.wconstructor.Constructor`
		"""
		constructors = self.api.get_constructors_of_class(class_name)
		constructors = list(map(lambda c: Constructor(c, self), constructors))
		return constructors

	def new_instance(self, class_name, params=[], param_types=None):
		"""
		Create a new instance of a given class.

		Can be used as method's param or a field's value.

		Examples:

		.. code-block:: python

		   agent.new_instance("int", [3])
		   agent.new_instance("double", [3.3])
		   agent.new_instance("java.lang.String", ['somestr'])
		   agent.new_instance("com.example.SomeClass", [[[1, 2], [3, 2]]], ['int[][]'])
		   agent.new_instance("com.example.SomeClass", [1, 1, '1', '1', False, 1, 1, 1],
		                                    ['java.lang.Integer', 'java.lang.Double', 'java.lang.Character',
		                                    'java.lang.String', 'java.lang.Boolean', 'java.lang.Byte',
		                                    'java.lang.Long', 'java.lang.Float'])
		   agent.new_instance("com.example.SomeClass", [agent.new_instance('java.lang.Integer', [3])])

		:param class_name: The full name of the class to create instance of
		:type class_name: str
		:param params: The constructor's parameters list
		:type params: list
		:param param_types: The constructor's parameters types list. This param is optional, if the constructor is overloaded you might need to specify the constructor param types.
		:type param_types: list
		:return: The new created instance
		:rtype: :py:class:`~marrs.frida.wrappers.winstance.Instance`
		"""
		if is_simple_array_type(class_name):
			raise ValueError("Use '{0}' function to create an array".format(self.new_array.__name__))

		if param_types is not None and len(params) != len(param_types):
			raise ValueError(
				"len(params) != len(param_types), className={0}, params={1}, param_types={2}".format(class_name, params,
				                                                                                     param_types))

		class_name = java_primitive_type_to_wrapper_class(class_name)

		params_data = self._get_params_data(params, param_types)
		instance_data = self.api.create_instance(class_name, params_data)
		return InstanceFactory.create(self, instance_data)

	def new_array(self, arr_type, arr_list):
		"""
		Create a new array instance.

		Can be used as method's param or a field's value.

		Examples:

		.. code-block:: python

		   agent.new_array("int[]", [1, 2, 3])
		   agent.new_array("int[][]", [[18, 2, 3], [12, 1, 1], [2, 2, 2]])
		   agent.new_array('java.lang.Integer[][][]', [[[1]], [[2], [9]], [[3]]])
		   agent.new_array("java.lang.Integer[]", [agent.new_instance('java.lang.Integer', [1]),
	                                               agent.new_instance('java.lang.Integer', [2]),
	                                               agent.new_instance('java.lang.Integer', [3])])


		:param arr_type: The type of the array.
		:type arr_type: str
		:param arr_list: The items of the array
		:type arr_list: list
		:return: The new created array
		:rtype: :py:class:`~marrs.frida.wrappers.warray.Array`
		"""
		if not is_simple_array_type(arr_type):
			raise ValueError("arr_type is not an array type")

		if not isinstance(arr_list, list):
			raise ValueError("The given arr_list must be of a list type")

		elem_type = extract_base_elem_type_from_simple_arr_type(arr_type)
		converted_elems = [self._convert_to_api_js_value(arr_list[i], elem_type) for i in range(len(arr_list))]

		arr_type = convert_to_api_class_name(arr_type)

		array_data = self.api.create_array(arr_type, converted_elems)
		return InstanceFactory.create(self, array_data)

	def __to_string__(self, instance_id):
		return self.api.to_string(instance_id)

	def __call_instance_method__(self, instance_id, method_name, params=[], param_types=[]):
		params_data = self._get_params_data(params, param_types)
		value_data = self.api.call_method(method_name, params_data, instance_id, None)
		return self._value_data_to_python_value(value_data)

	def call_static_method(self, class_name, method_name, params=[], param_types=[]):
		"""
		Call a static method of a class (and get the result value).

		Examples:

		.. code-block:: python

		   ret_val = agent.call_static_method("com.example.SomeClass", "someStaticMethod1", ["someStr"], ["java.lang.String"])
		   ret_val = agent.call_static_method("com.example.SomeClass", "someStaticMethod2", [1, 3], ['int', 'double'])
		   ret_val = agent.call_static_method("com.example.SomeClass", "someNotOverloadedMethod", ["someStr", 3])
		   ret_val = agent.call_static_method("com.example.SomeClass", "someNoParamsMethod")


		:param class_name: The name of the class
		:type class_name: str
		:param method_name: The name of the method to call to
		:type method_name: str
		:return: The return value of the method
		"""
		class_name = convert_to_api_class_name(class_name)
		params_data = self._get_params_data(params, param_types)
		value_data = self.api.call_method(method_name, params_data, None, class_name)
		return self._value_data_to_python_value(value_data)

	def get_static_field_value(self, class_name, field_name):
		"""
		Get the value of static field of a class.

		For example:

		.. code-block:: python

		   ret_val = agent.get_static_field_value("com.example.SomeClass", "someStaticFieldName")


		:param class_name: The name of the class
		:type class_name: str
		:param field_name: The name of the field to get its value
		:type field_name: str
		:return: The value of the field
		"""
		return self.__get_field_value__(class_name, field_name)

	def __get_field_value__(self, class_name, field_name, instance_id=None):
		class_name = convert_to_api_class_name(class_name)
		value_data = self.api.get_field_value(class_name, field_name, instance_id)
		return self._value_data_to_python_value(value_data)

	def set_static_field_value(self, class_name, field_name, new_value):
		"""
		Set the value of static field of a class.

		For example:

		.. code-block:: python

		   ret_val = agent.get_static_field_value("com.example.SomeClass", "someStaticFieldName")


		:param class_name: The name of the class
		:type class_name: str
		:param field_name: The name of the field to get set its value
		:type field_name: str
		:param new_value: The new value to set
		"""
		self.__set_field_value__(class_name, field_name, new_value)

	def __set_field_value__(self, class_name, field_name, new_value, instance_id=None):
		class_name = convert_to_api_class_name(class_name)
		value_to_set = self._convert_to_api_js_value(new_value)
		self.api.set_field_value(class_name, field_name, value_to_set, instance_id)

	def run_js(self, js_code):
		"""
		Run Javascript code and get the result.

		For example:

		.. code-block:: python

		   ret_val = agent.run_js("3+5")
		   assert(ret_val == 8)


		:param js_code: The Javascript code to run
		:type js_code: str
		:return: The result value
		"""
		value_data = self.api.run_js(js_code)
		return self._value_data_to_python_value(value_data)
