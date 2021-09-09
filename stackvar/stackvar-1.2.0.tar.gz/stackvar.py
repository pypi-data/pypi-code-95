import collections
import threading
from functools import wraps
import inspect
from typing import (
    Any,
    Callable,
    Dict,
)
from pydantic.typing import ForwardRef, evaluate_forwardref
from collections import namedtuple


class _Namespace:
    pass


class GLOBAL_NAMESPACE(_Namespace):
    namespace = 'global::'


class AUTO_NAMESPACE(_Namespace):
    pass


class DEFAULT_NAMESPACE(_Namespace):
    pass


def send(*namespaces, **stack_variables):
    if not namespaces:
        namespaces = [_storage.get_current_namespace()]
    namespaced_variables = {}
    for nspace in namespaces:
        for varn, value in stack_variables.items():
            namespaced_variables[_param_to_key(nspace, varn)] = value
    return _storage.send_variables(namespaced_variables)


def push_namespace(namespace, **stack_variables):
    stack_variables = {_param_to_key(namespace, n):v for n,v in stack_variables.items()}
    return _storage.send_variables(stack_variables, namespace)


def solve_namespace(receiver):
    # https://docs.python.org/3/library/inspect.html#types-and-members
    if isinstance(receiver, str):
        return receiver
    elif receiver == GLOBAL_NAMESPACE:
        return receiver.namespace
    elif hasattr(receiver, '__qualname__'):
        while hasattr(receiver, '__wrapped__'):
            receiver = receiver.__wrapped__
        qualname = receiver.__qualname__
        lineno = ''
        if hasattr(receiver, '__code__'):
            lineno = f'.{receiver.__code__.co_firstlineno}'
        return f'{receiver.__module__}.{qualname}{lineno}'
    elif type(type(receiver)) == type:
        return f'{receiver.__module__}.{receiver.__class__.__name__}'
    raise StackVarTypeError(f'Canno handle receiver type {type(receiver)}')


class Variable:
    pass


class Factory(Variable):
    pass


class receive:
    AUTO = AUTO_NAMESPACE
    GLOBAL = GLOBAL_NAMESPACE
    DEFAULT = DEFAULT_NAMESPACE
    def __init__(self, namespace=AUTO):
        self.namespace = namespace

    def _solve_namespace(self, method):
        if self.namespace == self.AUTO:
            return solve_namespace(method)
        elif self.namespace != self.DEFAULT:
            return solve_namespace(self.namespace)
        return _storage.get_current_namespace()

    def __call__(self, method):
        if not get_stack_variables(method):
            return method
        @wraps(method)
        def wrapper(*a, **kw):
            namespace = self._solve_namespace(method)
            variables = {_param_to_key(namespace, n):v for n,v in get_stack_variables(method).items()}
            pos_to_param  = tuple((pos, name) for name, (anno, value, pos) in variables.items())
            first_pos = pos_to_param[0][0]
            last_pos = pos_to_param[-1][0]
            pos_to_param = collections.OrderedDict(pos_to_param)
            ##
            passed = set()
            if first_pos < len(a):
                for pos in range(first_pos, max(last_pos + 1, len(a))):
                    if pos in pos_to_param:
                        passed.add(pos_to_param[pos])
            for n in kw:
                # if k is already in kw
                # the error will raise when calling the method (as if undecorated)
                # we don't care here
                passed.add(_param_to_key(namespace, n))
            non_passed = set(variables) - passed
            undeclared_diff = _storage.get_undeclared_diff(non_passed)
            if not undeclared_diff:
                # All variables are declared in the stackvar.namespace
                # No need to declare them in this scope
                for k in non_passed:
                    kw[_key_to_param(k)] = _storage[k]
                return method(*a, **kw)
            # Gather variables and values
            undeclared_variables = {}
            missing = []
            for k in undeclared_diff:
                anno, value, pos = variables[k]
                if value == inspect._empty:
                    # Gather non declared empty values (no default value)
                    # [(pos,name),...]
                    missing.append((variables[k][2], k))
                    continue
                if isinstance(anno, Factory):
                    # We declared the stack variable type as a factory
                    value = value()
                undeclared_variables[k] = value
            if missing:
                # Print in the right order
                missing = [repr(n) for _,n in sorted(missing)]
                # We try to mimic a standard TypeError output
                raise StackVarTypeError(f'{method.__name__}() missing {len(missing)} '
                                        'required positional stack variable'
                                        f'{"s" if len(missing) > 1 else ""}: {", ".join(missing)}')
            with _storage.send_variables(undeclared_variables):
                for k in non_passed:
                    kw[_key_to_param(k)] = _storage[k]
                return method(*a, **kw)
        return wrapper


def get_stack_variables(method: Callable[..., Any]) -> Dict[str, Any]:
    sign = _get_typed_signature(method)
    variables_dict = collections.OrderedDict()
    for pos, (param_name, param) in enumerate(sign.parameters.items()):
        if issubclass(param.annotation, Variable):
            variables_dict[param_name] = param.annotation, param.default, pos
    return variables_dict


def _get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    # From FastAPI (MIT License)
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=_get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def _get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    # From FastAPI (MIT License)
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


class StackVarLookupError(LookupError):
    pass


class StackVarTypeError(TypeError):
    pass


def _param_to_key(namespace, param_name):
    if not isinstance(namespace, str):
        namespace = solve_namespace(namespace)
    return f'{namespace}|{param_name}'


def _key_to_param(key):
    return key.split('|')[1]


_SentPack = namedtuple('_SentPack', 'namespace variables')


class _VariablesStorage:
    def __init__(self):
        self._thread_stacks = collections.defaultdict(list)

    def send_variables(self, variables_dict: Dict[str,Any], current_namespace=None):
        namespace = current_namespace or self.get_current_namespace()
        stack = self._thread_stacks[threading.get_ident()]
        length = len(stack) + 1
        last_pack = stack[-1] if stack else _SentPack(namespace, dict())
        class WithCtx:
            def __enter__(self):
                pack = _SentPack(namespace, last_pack.variables.copy())
                stack.append(pack)
                pack.variables.update(variables_dict)
                return variables_dict
            def __exit__(self, exc_type, exc_val, exc_tb):
                assert len(stack) == length, 'You must exit contexts in the correct order'
                stack.pop()
        return WithCtx()

    def get_current_namespace(self):
        stack = self._get_stack()
        if stack:
            return stack[-1].namespace
        return solve_namespace(GLOBAL_NAMESPACE)

    def _get_stack(self):
        return self._thread_stacks[threading.get_ident()]

    def _get_variables(self):
        stack = self._get_stack()
        return stack[-1].variables if stack else None

    def __getitem__(self, key):
        variables = self._get_variables()
        if variables:
            return variables[key]
        raise StackVarLookupError(f'stack variable {key!r} is not defined in thread scope')

    def __contains__(self, key):
        return key in self._get_variables()

    def get_undeclared_diff(self, keys):
        variables = self._get_variables()
        if variables:
            diff = keys - set(variables)
            return diff
        return keys


_storage = _VariablesStorage()


class _empty:
    pass


def _lookup(namespace: Any,
           name: str,
           default: Any=_empty) -> Any:
    namespace = namespace or _storage.get_current_namespace()
    key = _param_to_key(namespace, name)
    if key in _storage:
        return _storage[key]
    if default != _empty:
        return default
    raise StackVarLookupError(f'Stack variable {key!r} is not defined in thread scope')


def get(*args, **variables):
    """
    Examples:
        get(foo=10)                # lookup 'foo' stack variable in the global namespace, use 10 as default if missing
        get('mynamespace', foo=10) # same as above, but inside the namespace 'mynamespace'

        get('foo')                # lookup 'foo' stack variable in the global namespace, no default value
                                  # raises StackVarLookupError if not found
        get('mynamespace', 'foo') # same as above, but inside the namespace 'mynamespace'

    Note that when you provide a namespace it can be string or any object,
    as far as `stackvar.solve_namespace` can solve a string for it.
    """
    assert 0 <= len(args) <= 2, 'Only provide 0, 1 or 2 positional arguments'
    if not variables:
        assert args, 'Please provide arguments.'
        if len(args) == 1 and not variables:
            namespace = _storage.get_current_namespace()
            name = args[0]
            default = _empty
        elif len(args) == 2:
            namespace = args[0]
            name = args[1]
            default = _empty
    else:
        if len(args) == 1:
            namespace = args[0]
        else:
            # They are passing more than 1 positional arguments with kwargs present
            assert not args, 'Please provide 0 or 1 positional arguments when passing kwargs'
            namespace = _storage.get_current_namespace()
        if len(variables) == 1:
            name, default = next(iter(variables.items()))
        else:
            return tuple(_lookup(namespace, n, d) for n, d in variables.items())
    assert isinstance(name, str), f'Please provide variable name as string not {type(name)}'
    return _lookup(namespace, name, default)


class Namespace:
    def __init__(self, namespace=GLOBAL_NAMESPACE):
        self.namespace = namespace
    def __getattr__(self, name):
        key = _param_to_key(self.namespace, name)
        if key in _storage:
            return _storage[key]
        raise AttributeError(f'Stack variable {name!r} undefined')
    def __getitem__(self, name):
        key = _param_to_key(self.namespace, name)
        return _storage[key]
    def __contains__(self, name):
        key = _param_to_key(self.namespace, name)
        return key in _storage

