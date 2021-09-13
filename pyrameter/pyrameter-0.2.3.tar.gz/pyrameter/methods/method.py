"""Scaffolding to standardize optimization method development.

Classes
-------
Method
    Abstract class on which to develop optimization methods.
"""
import copy


class Method():
    """Abstract class on which to develop optimization methods.

    To create a new method, implement __init__ with custom intializaiton args
    and __call__ with the signature defined here.

    """
    def __call__(self, space):
        raise NotImplementedError
    
    @classmethod
    def from_json(cls, json_obj):
        """Load method state from a JSON object.

        If any fields in ``json_obj`` need to be reformatted (e.g. if they
        were converted to JSON-compatible format in ``to_json``), override
        this classmethod and do the conversion there, then pass the updated
        dictionary to the default method with
        ``super(<class>, cls).from_json(updated_obj)``, where ``<class>`` is
        the subclass overriding this method.

        Parameters
        ----------
        json_obj : dict
            Method state to load.
        """
        obj = cls()
        obj.__dict__.update(json_obj)
        return obj

    def to_json(self):
        """Convert method state to a JSON-compatible dictionary.

        The default implementation creates a deep copy of the Method object's
        state dictionary (``self.__dict__``) and returns that. If any
        attributes set in __init__ are not JSON-compatible, override this
        method and convert those attributes to a JSON-compatible format.
        """
        return copy.deepcopy(self.__dict__)
