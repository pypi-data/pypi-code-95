from .hook import Hook
from ..utils import convert_to_api_class_name


class HooksManager:
	def __init__(self, agent):
		self._agent = agent
		self._hooks = {}
		self._inc_id = 1

	def __repr__(self):
		return str(self._hooks)

	def __getitem__(self, key):
		return self._hooks[key]

	def disable(self, hook_id):
		self._agent.api.disable_hook(hook_id)
		self._hooks[hook_id].enabled = False

	def enable(self, hook_id):
		self._agent.api.enable_hook(hook_id)
		self._hooks[hook_id].enabled = True

	def call(self, hook_id, params, orig_retval):
		return self._hooks[hook_id].hook_impl(params, orig_retval)

	def add(self, class_name, method_name, param_types=None, hook_impl=None, get_original_retval=False,
	        show_output=False):
		if show_output:
			self._agent.output.start()

		hook_id = self._inc_id

		class_name = convert_to_api_class_name(class_name)
		if param_types:
			param_types = [convert_to_api_class_name(pt) for pt in param_types]

		if hook_impl is None:
			def default_hook_impl(params, original_retval):
				self._agent.__print__(params)
				return original_retval

			get_original_retval = True
			hook_impl = default_hook_impl

		def wrap_hook_func_with_args_convertion(hook_impl_func):
			def hook_impl_wrapper(args_json_list, original_retval):
				args = list(map(lambda arg_json: self._agent._value_data_to_python_value(arg_json), args_json_list))
				orig_retval_python = self._agent._value_data_to_python_value(original_retval)
				val = hook_impl_func(args, orig_retval_python)
				return val

			return hook_impl_wrapper

		hook_impl = wrap_hook_func_with_args_convertion(hook_impl)

		hook = Hook(self, hook_id, class_name, method_name, param_types, hook_impl, show_output)
		self._hooks[hook_id] = hook
		self._inc_id += 1

		self._agent.api.hook_method(hook_id, class_name, method_name, param_types, get_original_retval)

		return hook
