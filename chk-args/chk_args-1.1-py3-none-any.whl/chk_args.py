import inspect
from typing import get_type_hints, Any

def chk_args(func):
	spec = inspect.getfullargspec(func)
	annotations = spec.annotations

	def _chk_args(name, val):
		if name in annotations:
			if annotations[name] == Any:
				return val
			elif issubclass(type(val), annotations[name]):
				#サブクラスのとき
				return val
			elif type(val) != annotations[name]:
				if annotations[name] == float and type(val) == int:
					#floatにintが渡された
					return float(val)
				elif annotations[name] == int and type(val) == float and val - int(val) == 0:
					#intにn.0のfloatが渡された
					return int(val)
				raise TypeError(f"The type of argument ({name}) is {annotations[name]}.")
			else:
				return val

	def wrapper(*args, **kwargs):
		i = 0
		_args = list(args)
		for name, val in zip(spec.args, args):
			_args[i] = _chk_args(name, val)
			i += 1
		for key, val in zip(list(kwargs.keys()),list(kwargs.values())):
			kwargs[key] = _chk_args(key, val)
		return func(*_args, **kwargs)
	return wrapper


