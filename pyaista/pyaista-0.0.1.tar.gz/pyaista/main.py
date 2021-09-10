from typing import Any, List
from .error import AistaError

__all__ = ['AistaError', 'BaseDeployment']


class _BaseDeploymentType(type):

    def __new__(cls, name, bases, namespace):
        namespace['aista_methods'] = _BaseDeploymentType.__methods(namespace)
        namespace['methods'] = _BaseDeploymentType.__methods(namespace, is_aista_methods=False)
        return super().__new__(cls, name, bases, namespace)

    def __init__(self, name, bases, namespace):
        interface_methods = getattr(self, 'methods', [])
        for base in bases:
            for aista_method in getattr(base, 'aista_methods', []):
                if aista_method not in interface_methods:
                    raise AistaError(name, aista_method)

    def __methods(dct, is_aista_methods=True) -> List[str]:
        if is_aista_methods:
            return [k for k, v in dct.items() if callable(v) and getattr(v, '__isaistamethod__', False)]
        else:
            return [k for k, v in dct.items() if callable(v)]


def _aistamethod(method) -> Any:
    method.__isaistamethod__ = True
    return method


class BaseDeployment(metaclass=_BaseDeploymentType):

    @_aistamethod
    def main(self) -> Any:
        pass

    @staticmethod
    def aista_log(*values) -> None:
        print(*values)
