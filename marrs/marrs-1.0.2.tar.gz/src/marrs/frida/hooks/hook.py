class Hook:
	def __init__(self, hooks_manager, hook_id, class_name, method_name, param_types, hook_impl, show_output):
		self._hooks_manager = hooks_manager
		self.id = hook_id
		self.class_name = class_name
		self.method_name = method_name
		self.param_types = param_types
		self.hook_impl = hook_impl
		self.enabled = True
		self.show_output = show_output
		self.call_num = 0

	def __repr__(self):
		return "Hook(id='{0}', class='{1}', method='{2}', param_types='{3}', enabled={4}, show_output={5})".format(
			self.id,
			self.class_name,
			self.method_name,
			self.param_types,
			self.enabled,
			self.show_output)

	def enable(self):
		self._hooks_manager.enable(self.id)

	def disable(self):
		self._hooks_manager.disable(self.id)

	def inc_call_num(self):
		self.call_num += 1
		return self.call_num
