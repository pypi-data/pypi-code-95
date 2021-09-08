
from collections import namedtuple
from collections.abc import Mapping, Iterable
from typing import Optional, TypeVar, Hashable, \
	Dict, Iterable, Union, Tuple, List, Any, Generator

Cls = TypeVar('User Defined Class')

class DunderDecoratorException(Exception):

	def __init__(
			self,
			cls_obj: Cls,
			message: str,
			attr: Optional[str] = '',
	) -> None:
		self.cls_obj = cls_obj
		self.attr = attr
		self.message = message
		self.cls_obj_name_and_addr = (
			f'<{cls_obj.__module__}'
			+ f'.{cls_obj.__class__.__name__}'
			+ f' object at {hex(id(cls_obj))}>'
		)
		super().__init__(message)

	def __str__(self):
		if self.message == 'iterable':
			attr_type = getattr(
					self.cls_obj, self.attr
			).__class__.__name__ 
			iterable_attrs = []
			message = (
				f'\n\nAttribute "{self.attr}" belonging to '
				+ f'{self.cls_obj_name_and_addr} is\n'
				+ f'of type {attr_type}, which is not iterable. attr' 
				+ f' must be the name of an attribute\n'
				+ f'owned by {self.cls_obj_name_and_addr} '
				+ f'that is {self.message}.'
			)
			if hasattr(self.cls_obj, '__slots__'):
				message += (
					f'\nConsider setting slots to True.'
				)
				for attr in self.cls_obj.__slots__:
					value = getattr(self.cls_obj, attr)
					if isinstance(value, Iterable):
						iterable_attrs.append(attr)
			elif hasattr(self.cls_obj, '__dict__'):
				message += (
					f'\n\nConsider using dunder_iter without '
					+ f'any parameters, which will define __iter__\n'
					+ f'with repsect to '
					+ f'{self.cls_obj_name_and_addr}\'s __dict__.'
				)
				for attr, value in self.cls_obj.__dict__.items():
					if isinstance(value, Iterable):
						iterable_attrs.append(attr)
			if iterable_attrs:
				message = (
					f'{message[:-1]}, \nor setting '
					+ f'attr equal to the name of one\n'
					+ f'of {self.cls_obj_name_and_addr}\'s '
					+ f'iterable attributes.\n'
					+ f'A list of {self.cls_obj_name_and_addr}\'s '
					+ f'iterable \nattributes is provided below.\n'
					+ f'{iterable_attrs}'
				)

		elif self.message == 'indexable':
			attr_type = getattr(
					self.cls_obj, self.attr
			).__class__.__name__ 
			indexable_attrs = []
			message = (
				f'\n\nAttribute "{self.attr}" belonging to '
				+ f'{self.cls_obj_name_and_addr} is\n'
				+ f'of type {attr_type}, '
				+ f'which is not indexable. attr' 
				+ f' must be the name of an attribute\n'
				+ f'owned by {self.cls_obj_name_and_addr} '
				+ f'that is {self.message}.'
			)
			if hasattr(self.cls_obj, '__slots__'):
				message += (
					f'\nConsider setting slots to True.'
					+ f'if it is not already.'
				)
				for attr in self.cls_obj.__slots__:
					value = getattr(self.cls_obj, attr)
					if hasattr(value, '__getitem__'):
						indexable_attrs.append(attr)
			elif hasattr(self.cls_obj, '__dict__'):
				message += (
					f'\n\nConsider using dunder_iter without '
					+ f'any parameters, which will define __iter__\n'
					+ f'with repsect to '
					+ f'{self.cls_obj_name_and_addr}\'s __dict__.'
				)
				for attr, value in self.cls_obj.__dict__.items():
					if hasattr(value, '__getitem__'):
						indexable_attrs.append(attr)
			if indexable_attrs:
				message = (
					f'{message[:-1]}, \nor setting '
					+ f'attr equal to the name of one\n'
					+ f'of {self.cls_obj_name_and_addr}\'s '
					+ f'indexable attributes.\n'
					+ f'A list of {self.cls_obj_name_and_addr}\'s '
					+ f'indexable \nattributes is provided below.\n'
					+ f'{indexable_attrs}'
				)

		elif self.message == ('dict', 'iter'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__dict__".\n'
			)
			if hasattr(self.cls_obj, '__slots__'):
				message += (
					f'\nConsider setting slots to True.'
				)
				iterable_attrs = []
				for attr in self.cls_obj.__slots__:
					value = getattr(self.cls_obj, attr)
					if isinstance(value, Iterable):
						iterable_attrs.append(attr)
				if iterable_attrs:
					message = (
						f'{message[:-1]}, or setting '
						+ f'attr to the name of an iterable '
						+ f'attribute owned\nby '
						+ f'{self.cls_obj_name_and_addr}. '
						+ f'A list of {self.cls_obj_name_and_addr}\'s '
						+ f'iterable \nattributes is provided below.\n'
						+ f'{iterable_attrs}'
					)
		elif self.message == ('slots', 'iter'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__slots__".\n'
			)
			if hasattr(self.cls_obj, '__dict__'):
				message += (
					f'\nConsider using dunder_iter without '
					+ f'any parameters, which will define __iter__\n'
					+ f'with repsect to '
					+ f'{self.cls_obj_name_and_addr}\'s __dict__.'
				)
				iterable_attrs = [] 
				for attr, value in self.cls_obj.__dict__.items():
					if isinstance(value, Iterable):
						iterable_attrs.append(attr)
				if iterable_attrs:
					message = (
						f'{message[:-1]}, or setting attr '
						+ f'to the name of an iterable '
						+ f'attribute owned\nby '
						+ f'{self.cls_obj_name_and_addr}. '
						+ f'A list of {self.cls_obj_name_and_addr}\'s '
						+ f'iterable \nattributes is provided below.\n'
						+ f'{iterable_attrs}'
					)
		elif self.message == ('dict', 'setitem'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__dict__".\n'
			)
			if hasattr(self.cls_obj, '__slots__'):
				message += (
					f'\nConsider setting slots to True.'
				)
				indexable_attrs = []
				for attr in self.cls_obj.__slots__:
					value = getattr(self.cls_obj, attr)
					if hasattr(value, '__getitem__'):
						indexable_attrs.append(attr)
				if indexable_attrs:
					message = (
						f'{message[:-1]}, or setting attr '
						+ f'to the name of an indexable '
						+ f'attribute owned\nby '
						+ f'{self.cls_obj_name_and_addr}. '
						+ f'A list of {self.cls_obj_name_and_addr}\'s '
						+ f'indexable \nattributes is provided below.\n'
						+ f'{indexable_attrs}'
					)
		elif self.message == ('dict', 'getitem'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__dict__".\n'
			)
			if hasattr(self.cls_obj, '__slots__'):
				message += (
					f'\nConsider setting slots to True.'
				)
				indexable_attrs = []
				for attr in self.cls_obj.__slots__:
					value = getattr(self.cls_obj, attr)
					if hasattr(value, '__getitem__'):
						indexable_attrs.append(attr)
				if indexable_attrs:
					message = (
						f'{message[:-1]}, or setting attr '
						+ f'to the name of an indexable '
						+ f'attribute owned\nby {self.cls_obj_name_and_addr}. '
						+ f'A list of {self.cls_obj_name_and_addr}\'s '
						+ f'indexable \nattributes is provided below.\n'
						+ f'{indexable_attrs}'
					)
		elif self.message == ('dict', 'missing'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__dict__".\n'
			)
			indexable_attrs = []
			for attr in self.cls_obj.__slots__:
				value = getattr(self.cls_obj, attr)
				if hasattr(value, '__getitem__'):
					indexable_attrs.append(attr)
			if indexable_attrs:
				message = (
					f'{message}, Consider setting attr to the '
					+ f'name of an indexable '
					+ f'attribute owned\nby'
					+ f'{self.cls_obj_name_and_addr}. '
					+ f'A list of {self.cls_obj_name_and_addr}\'s '
					+ f'indexable \nattributes is provided below.\n'
					+ f'{indexable_attrs}'
				)
		elif self.message == ('dict', 'repr'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__dict__".\n'
			)
			if hasattr(self.cls_obj, '__slots__'):
				message += (
					f'\nConsider setting slots equal to True.'
				)
		elif self.message == ('slots', 'setitem'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__slots__".\n'
			)
			if hasattr(self.cls_obj, '__dict__'):
				message += (
					f'\nConsider using dunder_setitem without '
					+ f'any parameters, which will define __setitem__\n'
					+ f'with repsect to '
					+ f'{self.cls_obj_name_and_addr}\'s __dict__.'
				)
				indexable_attrs = [] 
				for attr, value in self.cls_obj.__dict__.items():
					if hasattr(value, '__getitem__'):
						indexable_attrs.append(attr)
				if indexable_attrs:
					message = (
						f'{message[:-1]}, or setting attr '
						+ f'to the name of an indexable '
						+ f'attribute owned\nby'
						+ f'{self.cls_obj_name_and_addr}. '
						+ f'A list of {self.cls_obj_name_and_addr}\'s '
						+ f'indexable \nattributes is provided below.\n'
						+ f'{indexable_attrs}'
					)
		elif self.message == ('attr_not_mapping_or_iterable'):
			attr_type = getattr(
					self.cls_obj, self.attr
			).__class__.__name__ 
			message = (
				f'attr must be the name of an attribute owned\n'
				+ f'by {self.cls_obj_name_and_addr} that is\n'
				+ f'mapping or iterable. Currently, attr is '
				+ f'set to {self.attr},\nwhich is of type'
				+ f'{attr_type}.'
			)
		elif self.message == ('slots', 'getitem'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__slots__".\n'
			)
			if hasattr(self.cls_obj, '__dict__'):
				message += (
					f'\nConsider using dunder_gettitem without '
					+ f'any parameters, which will define __getitem__\n'
					+ f'with repsect to '
					+ f'{self.cls_obj_name_and_addr}\'s __dict__.'
				)
				indexable_attrs = [] 
				for attr, value in self.cls_obj.__dict__.items():
					if hasattr(value, '__getitem__'):
						indexable_attrs.append(attr)
				if indexable_attrs:
					message = (
						f'{message[:-1]}, or setting attr '
						+ f'to the name of an indexable '
						+ f'attribute owned\nby '
						+ f'{self.cls_obj_name_and_addr}. '
						+ f'A list of {self.cls_obj_name_and_addr}\'s '
						+ f'indexable \nattributes is provided below.\n'
						+ f'{indexable_attrs}'
					)
		elif self.message == ('slots', 'repr'):
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f' has no attribute  "__slots__".\n'
			)
			if hasattr(self.cls_obj, '__dict__'):
				message += (
					f'\nConsider using dunder_repr without '
					+ f'any parameters, which will define __repr__\n'
					+ f'with repsect to '
					+ f'{self.cls_obj_name_and_addr}\'s __dict__.'
				)
		elif self.message == 'key_not_hashable':
			attr_type = self.attr.__class__.__name__ 
			message = (
				f'Provided key is of type {attr_type}, '
				+ f'which is not hashable.'
			)
		elif self.message == 'no_keys_method':
			attr_type = getattr(
					self.cls_obj, self.attr
			).__class__.__name__ 
			key_meth_attrs = []
			if hasattr(self.cls_obj, '__dict__'):
				for attr, value in self.cls_obj.__dict__.items():
					if hasattr(value, 'keys'):
						key_meth_attrs.append(attr)
			elif hasattr(self.cls_obj, '__slots__'):
				for attr, in self.cls_obj.__slots__:
					if hasattr(
						getattr(self.cls_obj, attr),
						'keys'
					):
						key_meth_attrs.append(attr)
			message = (
				f'{self.cls_obj_name_and_addr}\'s'
				+ f' attribute "{self.attr}"\nis of '
				+ f'type {attr_type}, '
				+ f'which is does not have a "keys" method.'
				+ f'\nBelow is a list of '
				+ f'{self.cls_obj_name_and_addr}\'s'
				+ f' attributes with key methods.'
				+ f'\n{key_meth_attrs}' 

			)
		elif self.message == 'key_not_in_obj_dict':
			keys = list(self.cls_obj.__dict__.keys())
			message = (
				f'Provided key is not in {self.cls_obj_name_and_addr}'
				+ f' \'s __dict__.\n If using the dunder_missing '
				+ f'decorator, make it is below the dunder_getitem'
				+ f' decorator. Below is a list of keys in '
				+ f'{self.cls_obj_name_and_addr}\'s __dict__.\n{keys}' 
			)
		elif self.message == 'key_not_in_obj_slots':
			keys = list(self.cls_obj.__slots__)
			message = (
				f'Provided key is not in {self.cls_obj_name_and_addr}'
				+ f' \'s __slots__.\n If using the dunder_missing '
				+ f'decorator, make it is below the dunder_getitem '
				+ f'decorator. Below is a list of keys in '
				+ f'{self.cls_obj_name_and_addr}\'s __slots__.\n{keys}' 
			)
		elif self.message == 'key_not_found':
			keys = list(getattr(self.cls_obj, self.attr).keys())
			message = (
				f'Provided key is not in {self.attr}\'s'
				+ f' dictionary.\nIf using the dunder_missing '
				+ f'decorator, make it is below the dunder_getitem ' 
				+ f'decorator. \nBelow is a list of '
				+ f'{self.cls_obj_name_and_addr}\'s attribute '
				+ f'{self.attr}\'s keys.\n{keys}' 
			)
		elif self.message == 'index_out_of_bounds':
			message = (
				f'Provided index is out of bounds.'			
			)
		elif self.message == 'missing_with_slots':
			message = (
				f'Cannot decorate a class that '
				+ f'uses __slots__ with dunder__missing\n'
				+ f'when attr is set to None.'
			)
		elif self.message == 'slots_immutable':
			message = (
				f'\n{self.cls_obj_name_and_addr} '
				+ f'uses __slots__ instead of __dict__ '
				+ f'to store it\'s attributes, which '
				+ f'means you cannot\n'
				+ f'add new attributes to '
				+ f'{self.cls_obj_name_and_addr} '
				+ f'post object creation.'
			)
		return message 

