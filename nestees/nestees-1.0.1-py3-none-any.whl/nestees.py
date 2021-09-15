'''Helper functions for dealing with deeply nested dictionaries.'''
from typing import Union, Any, Sequence, Mapping
from fieldpath import split_field_path

class Sentinel(object):
    '''Sentinel objects used to signal special handling.'''

    __slots__ = ("description",)

    def __init__(self, description) -> None:
        self.description = description

    def __repr__(self):
        return "Sentinel: {}".format(self.description)

DELETE_FIELD = Sentinel("Value used to delete a field in a document.")


def hasindex(arg):
    return isinstance(arg, Sequence) and not isinstance(arg, str)


def deep_get(dict_of_dicts: dict, field_path: Union[Sequence[str], str], default_value: Any = None) -> Any:
    '''
    Get a potentially nested value from a dictionary, or returns a default value
    Args:
        data (Dict[str, Any]): The (possibly nested) data.
        field_path (str): A field path (backtick escaped, dot delimited list of field names).
        default_value (Any): The value to return if data at the given path does not exist
    Returns:
        Any: (A copy of) the value stored for the ``field_path``.

    Supports Google's field_path notation (see firestore SDK)
    https://googleapis.dev/python/firestore/1.4.0/_modules/google/cloud/firestore_v1/field_path.html

    If the data is nested, for example:

    .. code-block:: python
       >>> data
       {
           'top1': {
               'middle2': {
                   'bottom3': 20,
                   'bottom4.has.dots': 22,
               },
               'middle5': True,
           }
       }
       >>> deep_get(data, 'top1.middle2.`bottom4.has.dots`')
       22

       >>> deep_get(data, 'my.road.to.nowhere`', 'ends here')
       'ends here'
    '''
    deep_data = dict_of_dicts
    for field_name in split_field_path(field_path):
        if isinstance(deep_data, Mapping):
            deep_data = deep_data.get(field_name)        
    
        if deep_data is None:
            return default_value
    
    return deep_data


def deep_set(dict_of_dicts: dict, field_path: Union[Sequence[str], str], value: Any) -> None:
    '''
    Sets a value at a potentially nested path in a dictionary.
    Supports Google's field_path notation (see firestore SDK)
    https://googleapis.dev/python/firestore/1.4.0/_modules/google/cloud/firestore_v1/field_path.html

    Args:
        data (Dict[str, Any]): The (possibly nested) data.
        field_path (str): A field path (backtick escaped, dot delimited list of field names).
        value (Any): The value to set at the given path.

    If the data is nested, for example:

    .. code-block:: python
       >>> data
       {
           'top': {}
       }

       >>> deep_set(datam, 'top.middle.`bottom.has.dots`', 'pongo')
       >>> data
       {
           'top': {
               'middle': {
                   'bottom.has.dots': 'pongo'
               }
           }
       }
    '''
    if DELETE_FIELD.description == getattr(value, 'description', ''):
        deep_delete(dict_of_dicts, field_path)
        return

    field_names = split_field_path(field_path)
    leaf_key = field_names[-1]
    
    for field_name in field_names[:-1]:
        dict_of_dicts = dict_of_dicts.setdefault(field_name, {})

    dict_of_dicts[leaf_key] = value
    

def deep_update(dict_of_dicts: dict, field_path: Union[Sequence[str], str], value: dict) -> None:
    '''
    Sets or updates an island at a potentially nested path in a dictionary.
    Applies the same logic as Python's built-in dict.update() method, 
    but with support for nested paths.

    Args:
        data (Dict[str, Any]):  The (possibly nested) data.
        field_path (str):       A field path (backtick escaped, dot delimited list of field names).
        value (Any):            The value to set or update at the given path.

    .. code-block:: python
       >>> data
       {
           'top': 53
       }

       >>> deep_update(data, 'top.middle', {'name':'John', 'occupation':'CEO'})
       >>> data
       {
           'top': {
               'middle': {
                    'name':'John',
                    'occupation':'CEO'
               }
           }
       }

       >>> deep_update(data, 'top.middle', {'gender':'male'})
       >>> data
       {
           'top': {
               'middle': {
                    'name':'John',
                    'occupation':'CEO',
                    'gender':'male'
               }
           }
       }

       >>> deep_update(data, 'top.middle', 53)
       >>> data
       {
           'top': {
               'middle': 53
           }
       }
    '''
    if DELETE_FIELD.description == getattr(value, 'description', ''):
        deep_delete(dict_of_dicts, field_path)
        return

    field_names = split_field_path(field_path)
    deep_data = dict_of_dicts

    for field_name in field_names:
        next_data = deep_data.setdefault(field_name, {})
        if not isinstance(next_data, Mapping):
            deep_data[field_name] = next_data = {}
        deep_data = next_data 

    deep_data.update(value)


def deep_delete(dict_of_dicts: dict, field_path: Union[Sequence[str], str]) -> None:
    '''Removes a value at a potentially nested path in a dictionary.
    Supports Google's field_path notation (see firestore SDK)
    https://googleapis.dev/python/firestore/1.4.0/_modules/google/cloud/firestore_v1/field_path.html

    '''
    field_names = split_field_path(field_path)
    for field_name in field_names[:-1]:
        dict_of_dicts = dict_of_dicts.get(field_name, None)
        if dict_of_dicts is None:
            return
    dict_of_dicts.pop(field_names[-1], 1)