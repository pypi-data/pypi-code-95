'''
By Andy Stokely
'''

from collections import namedtuple
from collections.abc import Mapping, Iterable
from typing import Optional, TypeVar, Hashable, \
	Dict, Iterable, Union, Tuple, List, Any, Generator
from .exceptions import DunderDecoratorException 

Cls = TypeVar('User Defined Class')


def dunder_iter(
		cls: Optional[Cls] = None, 
		attr: Optional[str] = None,
		slots: Optional[bool] = None,
) -> Cls:
	"""
	Adds an __iter__ special method to the decorated class.

	Parameters
	---------
	cls : User Defined Class
		Class that is decorated

	attr : str, optional
		Name of class object attribute that __iter__
		is defined with repect to. If None, dunder_iter 
		defines __iter__ with respect to the class object's
		__dict__ or __slots__. Defaults to None.

	slots : bool, optional
		If True, dunder_iter defines __iter__ with respect to
		the class object's __slots__ attribute. Else, __iter__
		is defined with respect to the class object's dictionary
		or attribute specified by attr. Defaults to None.

	Returns
	-------
	: User Defined Class

	Examples
	--------
	Add an __iter__ method to a class and have 
	it defined with respect to the class object's
	dictionary.

	>>> @dunder_iter
	>>> Class A(object):
	>>>		pass
	>>> a = A()
	>>> a.a = 1
	>>> a.b = 2
	>>> a.c = 3
	>>> for i in a:
	>>> 	print(i)
		1
		2	
		3
	
	Add an __iter__ method to a class and have 
	it defined with respect to one of the class
	objects iterable attributes.

	>>> @dunder_iter(attr='a')
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A([1, 2, 3])
	>>> for i in a:
	>>> 	print(i)
		1
		2	
		3

	Add an __iter__ method to a class and have it
	defined with repsect to the class's __slots__
	attribute. 

	>>> @dunder_iter(slots=True)
	>>> Class A(object):
	>>>		__slots__=('a', 'b', 'c')
	>>>		def __init__(self, a, b, c):
	>>>			self.a = a	
	>>>			self.b = b	
	>>>			self.c = c	
	>>> a = A(1, 2, 3)
	>>> for i in a:
	>>> 	print(i)
		1
		2	
		3

	"""
	def wrap(
			cls: Cls,
	) -> Cls:
		if attr is None:
			if slots is None:
				def __iter__(
						cls: Cls
				) -> Generator:
					if hasattr(cls, '__dict__'):
						for attr, value in cls.__dict__.items():
							yield attr, value
					else:
						raise DunderDecoratorException(
							cls, ('dict', 'iter')
						) 
				setattr(cls, '__iter__', __iter__)
			else:
				def __iter__(
						cls: Cls
				) -> Generator:
					if hasattr(cls, '__slots__'):
						for attr in cls.__slots__:
							yield attr, getattr(cls, attr) 
					else:
						raise DunderDecoratorException(
							cls, ('slots', 'iter')
						) 
				setattr(cls, '__iter__', __iter__)
		else:
			def __iter__(
					cls: Cls
			) -> Generator:
				iter_attr = getattr(cls, attr)
				if isinstance(iter_attr, Mapping):
					for key, value in iter_attr.items():
						yield key, value
				elif isinstance(iter_attr, Iterable):
					for i in iter_attr:
						yield i 
				else:
					raise DunderDecoratorException(
						cls, 
						'iterable', 
						attr
					) 
			setattr(cls, '__iter__', __iter__)
		return cls
	if cls is None:
		return wrap 
	return wrap(cls)

def dunder_setitem(
		cls: Optional[Cls] = None, 
		attr: Optional[str] = False, 
		slots: Optional[bool] = None,
) -> Cls:
	"""
	Adds a __setitem__ special method to the decorated class.

	Parameters
	---------
	cls : User Defined Class
		Class that is decorated

	attr : str, optional
		Name of class object attribute that __setitem__
		is defined with repect to. The attribute is required
		to either be a mapping or an iterable. If the attribute is
		a mapping, the key used is one of the mapping's hash keys.
		If the attribute is an iterable, the key is an index. If the 
		index is out of bounds, the value is automatically appended to
		the left or right end of the iterable, depending on the value of
		the key. If None, dunder_setitem defines __setitem__ with 
		respect to the class object's __dict__ or __slots__. 
		Defaults to None.

	slots : bool, optional
		If True, dunder_setitem defines __setitem__ with respect to
		the class object's __slots__ attribute. Else, __setitem__
		is defined with respect to the class object's dictionary
		or attribute specified by attr. Defaults to None.

	Returns
	-------
	: User Defined Class

	Examples
	--------
	Add a __setitem__ method to a class and have 
	it defined with respect to the class object's
	dictionary.

	>>> @dunder_setitem
	>>> Class A(object):
	>>>		pass
	>>> a = A()
	>>> a['a'] = 1
	>>> print(a.a)
		1
	
	Add a __setitem__ method to a class and have 
	it defined with respect to one of the class
	objects iterable attributes.
	
	>>> @dunder_setitem(attr='a')
		#where the attribute is a non-mapping iterable
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A([1, 2, 3])
	>>> a[1] = 1
	>>> print(a.a)
		[1, 1, 3]
	>>> 
	>>> @dunder_setitem(attr='a')
		#where the attribute is a mapping
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A({'a' : 1, 'b' : 2, 'c' : 3})
	>>> a['a'] = 0
	>>> print(a.a)
		{'a' : 0, 'b' : 2, 'c' : 3}

	Add a __setitem__ method to a class and have it
	defined with repsect to the class's __slots__
	attribute. 

	>>> @dunder_setitem(slots=True)
	>>> Class A(object):
	>>>		__slots__=('a', 'b', 'c')
	>>>		def __init__(self, a, b, c):
	>>>			self.a = a	
	>>>			self.b = b	
	>>>			self.c = c	
	>>> a = A(1, 2, 3)
	>>> a['a'] = 5
	>>> print(a.a)
		5

	"""
	def wrap(
			cls: Cls,
	) -> Cls:
		if attr:
			def __setitem__(
					cls: Cls, 
					key: Hashable, 
					value: Any,
			) -> None:
				if isinstance(
					key,
					Hashable
				): 
					if hasattr(
						getattr(cls, attr), 
						'__getitem__'
					):
						if isinstance(
							getattr(cls, attr), 
							Mapping
						):
							print(True)
							getattr(cls, attr)[key] = value

						elif isinstance(
							getattr(cls, attr), 
							Iterable	
						):
							attr_size = len(
								getattr(cls, attr)
							) 
							if key >= 0:
								if key < attr_size:
									getattr(cls, attr)[key] = value
								else:
									tmp_iterable = [
										getattr(cls, attr)[i]
										if i < attr_size else
										0 for i in range(attr_size + 1)
									]
									tmp_iterable[-1] = value	
									setattr(cls, attr, tmp_iterable)
							else:
								abs_index = attr_size + key
								if abs_index >= 0:
									getattr(cls, attr)[abs_index] = (
										value
									)
								else:
									tmp_iterable = [
										0 if i == 0 
										else getattr(cls, attr)[i-1]
										for i in range(attr_size + 1)
									]	
									tmp_iterable[0] = value	
									setattr(cls, attr, tmp_iterable)
						else:
							raise DunderDecoratorException(
								cls, 
								'attr_not_mapping_or_iterable', 
								attr
							)
					else:
						raise DunderDecoratorException(
							cls, 
							'indexable', 
							attr
						) 
				else:
					raise DunderDecoratorException(
						cls, 
						'key_not_hashable', 
						key
					)
				return
			setattr(cls, '__setitem__', __setitem__)
		else:
			if slots is None:
				def __setitem__(
						cls: Cls, 
						key: Hashable, 
						value: Any,
				) -> None:
					if isinstance(
						key,
						Hashable
					): 
						if hasattr(cls, '__dict__'):
							cls.__dict__[key] = value
						else:
							raise DunderDecoratorException(
								cls, ('dict', 'setitem'), attr
							)
					else:
						raise DunderDecoratorException(
							cls, 
							'key_not_hashable', 
							key
						)
					return
				setattr(
					cls, 
					'__setitem__', 
					__setitem__
				)
			else:
				def __setitem__(
						cls: Cls, 
						key: str, 
						value: Any,
				) -> None:
					if hasattr(cls, '__slots__'):
						if hasattr(cls, key):
							setattr(cls, key, value)
						else:
							raise DunderDecoratorException(
								cls, 'slots_immutable', attr
							)
					else:
						raise DunderDecoratorException(
							cls, ('slots', 'setitem'), attr
						)
					return
				setattr(
					cls, 
					'__setitem__', 
					__setitem__
				)
		return cls
	if cls is None:
		return wrap 
	return wrap(cls)

def dunder_getitem(
		cls: Optional[Cls] = None, 
		attr: Optional[str] = False,
		slots: Optional[bool] = None,
) -> Cls:
	"""
	Adds a __getitem__ special method to the decorated class.

	Parameters
	---------
	cls : User Defined Class
		Class that is decorated

	attr : str, optional
		Name of class object attribute that __getitem__
		is defined with repect to. The attribute is required
		to either be a mapping or an iterable. If the attribute is
		a mapping, the key used is one of the mapping's hash keys.
		If the attribute is an iterable, the key is an index. If the 
		If None, dunder_getitem defines __getitem__ with 
		respect to the class object's __dict__ or __slots__. 
		Defaults to None.

	slots : bool, optional
		If True, dunder_getitem defines __getitem__ with respect to
		the class object's __slots__ attribute. Else, __getitem__
		is defined with respect to the class object's dictionary
		or attribute specified by attr. Defaults to None.

	Returns
	-------
	: User Defined Class

	Examples
	--------
	Add a __getitem__ method to a class and have 
	it defined with respect to the class object's
	dictionary.

	>>> @dunder_getitem
	>>> Class A(object):
	>>>		pass
	>>> a = A()
	>>> a.a = 1
	>>> print(a['a'])
		1
	
	Add a __getitem__ method to a class and have 
	it defined with respect to one of the class
	objects iterable attributes.
	
	>>> @dunder_getitem(attr='a')
		#where the attribute is a non-mapping iterable
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A([1, 2, 3])
	>>> print(a[2])
		3
	>>> 
	>>> @dunder_getitem(attr='a')
		#where the attribute is a mapping
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A({'a' : 1, 'b' : 2, 'c' : 3})
	>>> print(a['a'])
		1

	Add a __getitem__ method to a class and have it
	defined with repsect to the class's __slots__
	attribute. 

	>>> @dunder_setitem(slots=True)
	>>> Class A(object):
	>>>		__slots__=('a', 'b', 'c')
	>>>		def __init__(self, a, b, c):
	>>>			self.a = a	
	>>>			self.b = b	
	>>>			self.c = c	
	>>> a = A(1, 2, 3)
	>>> print(a['a'])
		1

	"""
	def wrap(
			cls: Cls,
	) -> Cls:
		if attr:
			if hasattr(cls, '__missing__'):
				def __getitem__(
						cls: Cls, 
						key: Hashable
				) -> Any:
					if isinstance(
						key,
						Hashable
					): 
						if hasattr(
							getattr(cls, attr), 
							'keys'
						):
							if key in getattr(cls, attr).keys():
								return getattr(cls, attr)[key]
							cls.__missing__(key)
							return getattr(cls, attr)[key]
						else:
							raise DunderDecoratorException(
								cls, 
								'no_keys_method', 
								attr
							)
					else:
						raise DunderDecoratorException(
							cls, 
							'key_not_hashable', 
							key	
						)
				setattr(cls, '__getitem__', __getitem__)
			else:
				def __getitem__(
						cls: Cls, 
						key: Hashable
				) -> Any:
					if isinstance(
						key,
						Hashable
					): 
						if hasattr(
							getattr(cls, attr), 
							'__getitem__'
						):
							if isinstance(
								getattr(cls, attr), 
								Mapping
							):
								if key in getattr(cls, attr):
									return getattr(cls, attr)[key]
								else:
									raise DunderDecoratorException(
										cls, 
										'key_not_found', 
										attr
									)
							elif isinstance(
								getattr(cls, attr), 
								Iterable	
							):
								if key < len(getattr(cls, attr)):
									return getattr(cls, attr)[key]
								else:
									raise DunderDecoratorException(
										cls, 
										'index_out_of_bounds', 
										attr
									)
						else:
							raise DunderDecoratorException(
								cls, 
								'indexable', 
								attr
							) 
					else:
						raise DunderDecoratorException(
							cls, 
							'key_not_hashable', 
							key	
						)
				setattr(cls, '__getitem__', __getitem__)
		else:
			if hasattr(cls, '__missing__'):
				if slots is None:
					def __getitem__(
							cls: Cls, 
							key: Hashable
					) -> Any:
						if hasattr(cls, '__dict__'):
							if isinstance(
								key,
								Hashable
							): 
								if key in cls.__dict__.keys():
									return cls.__dict__[key]
								cls.__missing__(key)
								return cls.__dict__[key]
							else:
								raise DunderDecoratorException(
									cls, 
									'key_not_hashable', 
									key	
								)
						else:
							raise DunderDecoratorException(
								cls,
								('dict', 'getitem'),
								attr
							)
				else:
					raise DunderDecoratorException(
						cls, 
						'missing_with_slots', 
						attr
					)
				setattr(cls, '__getitem__', __getitem__)
			else:
				if slots is None:
					def __getitem__(
							cls: Cls, 
							key: Hashable,
					) -> Any:
						if hasattr(cls, '__dict__'):
							if isinstance(
								key,
								Hashable
							): 
								if key in cls.__dict__.keys():
									return cls.__dict__[key]
								else:
									raise DunderDecoratorException(
										cls, 
										'key_not_in_obj_dict', 
										key	
									)
							else:
								raise DunderDecoratorException(
									cls, 
									'key_not_hashable', 
									key	
								)
						else:
							raise DunderDecoratorException(
								cls,
								('dict', 'getitem'),
								attr
							)
					setattr(
						cls, 
						'__getitem__', 
						__getitem__
					)
				else:
					def __getitem__(
							cls: Cls, 
							key: Hashable,
					) -> Any:
						if hasattr(cls, '__slots__'):
							if isinstance(
								key,
								Hashable
							): 
								if key in cls.__slots__:
									return getattr(cls, key) 
								else:
									raise DunderDecoratorException(
										cls, 
										'key_not_in_obj_slots', 
										key	
									)
							else:
								raise DunderDecoratorException(
									cls, 
									'key_not_hashable', 
									key	
								)
						else:
							raise DunderDecoratorException(
								cls,
								('slots', 'getitem'),
								attr
							)
					setattr(
						cls, 
						'__getitem__', 
						__getitem__
					)
		return cls
	if cls is None:
		return wrap 
	return wrap(cls)

def dunder_missing(
		cls: Optional[Cls] = None, 
		attr: Optional[str] = False,
		default_value: Optional[Any] = None,	
) -> Any:
	"""
	Adds a __missing__ special method to the decorated class.
	Must be used alongside the dunder_getitem decorator and
	declared first (below the dunder_getitem decorator).	

	Parameters
	---------
	cls : User Defined Class
		Class that is decorated

	attr : str, optional
		Name of class object attribute that __missing__
		is defined with repect to. The attribute is required
		to be a mapping. If None, dunder_getitem defines 
		__missing__ with respect to the class object's 
		dictionary. Defaults to None.

	default_value : Any, optional
		Value that is mapped to the "non-existent" key __missing__
		adds to the class object's dictionary or mapping attribute
		specified by attr. Defaults to None. 


	Returns
	-------
	: Any 

	Examples
	--------
	Add a __missing__ method to a class and have 
	it defined with respect to the class object's
	dictionary.

	>>> @dunder_getitem
	>>> @dunder_missing
	>>> Class A(object):
	>>>		pass
	>>> a = A()
	>>> a['a']
	>>> print(a['a'])
		None

	Add a __missing__ method to a class and have 
	it defined with respect to the class object's
	dictionary with a default value of 6.559.

	>>> @dunder_getitem
	>>> @dunder_missing
	>>> Class A(object):
	>>>		pass
	>>> a = A()
	>>> a['a']
	>>> print(a['a'])
		6.559
	
	Add a __missing__ method to a class and have 
	it defined with respect to one of the class
	objects mapping attributes.
	
	>>> @dunder_missing(attr='a')
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A({'a' : 1})
	>>> a['b']
	>>> print(a.a)
		{'a' : 1, 'b' : None}

	Add a __missing__ method to a class and have 
	it defined with respect to one of the class
	objects mapping attributes with a default
	value of [1, 2, 3, 4, 5].
	
	>>> @dunder_missing(attr='a', default_value=[1, 2, 3, 4, 5])
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A({'a' : 1})
	>>> a['b']
	>>> print(a.a)
		{'a' : 1, 'b' : [1, 2, 3, 4, 5]}

	"""
	def wrap(
			cls: Cls,
	) -> Cls:
		setattr(
			cls, 
			'__default_value', 
			default_value 
		)
		if attr:
			def __missing__(
					cls: Cls, 
					key: Hashable,
			) ->None:
				if hasattr(getattr(cls, attr), '__getitem__'):
					if isinstance(
						key,
						Hashable
					): 
						getattr(cls, attr)[key] = (
							cls.__default_value
						)
						return
					else:
						raise DunderDecoratorException(
							cls, 
							'key_not_hashable', 
							key	
						)
				else:
					raise DunderDecoratorException(
						cls, 
						'indexable', 
						attr
					) 
			setattr(cls, '__missing__', __missing__)
		else:
			def __missing__(
					cls: Cls, 
					key: Hashable,
			) ->None:
				if hasattr(cls, '__dict__'):
					if isinstance(
						key,
						Hashable
					): 
						cls.__dict__[key] = (
							cls.__default_value
						)
					else:
						raise DunderDecoratorException(
							cls, 
							'key_not_hashable', 
							key	
						)
				else:
					raise DunderDecoratorException(
						cls,
						('dict', 'missing'),
						attr
					)
				return
			setattr(cls, '__missing__', __missing__)
		return cls
	if cls is None:
		return wrap 
	return wrap(cls)

def dunder_repr(
		cls: Optional[Cls] = None, 
		slots: Optional[bool] = None,
) -> str:
	"""
	Adds a __repr__ special method to the decorated class.

	Parameters
	---------
	cls : User Defined Class
		Class that is decorated

	slots : bool, optional
		If True, dunder_repr defines __repr__ with respect to
		the class object's __slots__ attribute. Else, __repr__
		is defined with respect to the class object's dictionary.
		Defaults to None.

	Returns
	-------
	: str 

	Examples
	--------
	Add a __repr__ method to a class and have 
	it defined with respect to the class object's
	dictionary.

	>>> @dunder_repr
	>>> Class A(object):
	>>>		def __init__(self, a):
	>>>			self.a = a	
	>>> a = A(1)
	>>> print(a)
		A(a=1)
	>>> a.b = 5.662
	>>> print(a)
		A(a=1, b=5.662)
	>>> a.c = [1, 2, 3, 4, 5] 
	>>> print(a)
		A(a=1, b=5.662, c=[1, 2, 3, 4, 5])

	Add a __missing__ method to a class and have 
	it defined with respect to the class object's
	__slots__ attribute

	>>> @dunder_repr(slots=True)
	>>> Class A(object):
	>>>		__slots__=('a', 'b', 'c')
	>>>		def __init__(self, a, b, c):
	>>>			self.a = a	
	>>>			self.b = b	
	>>>			self.c = c	
	>>> a = A(1, 5.662, [1, 2, 3, 4, 5])
	>>> print(a)
		A(a=1, b=5.662, c=[1, 2, 3, 4, 5])
	>>> a.b = 6.332
	>>> print(a)
		A(a=1, b=6.332, c=[1, 2, 3, 4, 5])
	>>> a.c = 6
	>>> print(a)
		A(a=1, b=6.332, c=6)

	"""
	def wrap(
			cls: Cls,
	) -> Cls:
		if slots is None:
			def __repr__(cls) -> Dict:
				if hasattr(cls, '__dict__'):
					repr_cls_dict = {
						(
							attr if not str(attr)[0].isdigit() 
							else f'{attr.__class__.__name__}_{attr}'
						) : value for attr, value 
						in cls.__dict__.items()
					}
					ReprNamedTuple = namedtuple(
						cls.__class__.__name__, 
						repr_cls_dict
					)
					repr_namedtuple = ReprNamedTuple(
						**repr_cls_dict
					)
					return str(repr_namedtuple)
				else:
					raise DunderDecoratorException(
						cls,
						('dict', 'repr'),
					)
			setattr(cls, '__repr__', __repr__)
		else:
			def __repr__(cls) -> Dict:
				if hasattr(cls, '__slots__'):
					repr_cls_dict = {
						attr : getattr(cls, attr) 
						for attr in cls.__slots__
					}
					ReprNamedTuple = namedtuple(
						cls.__class__.__name__, 
						repr_cls_dict
					)
					repr_namedtuple = ReprNamedTuple(
						**repr_cls_dict
					)
					return str(repr_namedtuple)
				else:
					raise DunderDecoratorException(
						cls,
						('slots', 'repr'),
					)
			setattr(cls, '__repr__', __repr__)
		return cls
	if cls is None:
		return wrap 
	return wrap(cls)

