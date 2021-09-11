class Injector:
    """Class used for depenedency injection"""

    _scopeds = {}
    _singletons = {}

    def add_scoped(self, *args, **kwargs):
        """Adds an scoped type to the injector service"""
        obj_type = args[0][0] if isinstance(args[0], tuple) else args[0]
        if obj_type in self._singletons:
            raise InjectorError(f"class {obj_type} is already as Singleton")
        self._scopeds[obj_type] = _Instantiable(*args, **kwargs)

    def add_singleton(self, *args, **kwargs):
        """Adds a singleton type to the injector service"""
        obj_type = args[0][0] if isinstance(args[0], tuple) else args[0]
        if obj_type in self._scopeds:
            raise InjectorError(f"class {obj_type} is already as Scoped")
        self._singletons[obj_type] = _Instantiable(*args, **kwargs)

    def get_scoped(self, obj_type):
        """Returns a new instance for the class"""
        if obj_type in self._scopeds:
            return self._scopeds[obj_type].get(self)
        return None

    def get_singleton(self, obj_type):
        """Returns an instance that it's already created"""
        if obj_type in self._singletons:
            return self._singletons[obj_type]
        return None

    def get(self, obj_type):
        instance = self.get_scoped(obj_type)
        if instance is None:
            instance = self.get_singleton(obj_type)
        return instance

    def clear(self):
        self._scopeds = {}
        self._singletons = {}


class _Instantiable:
    def __init__(self, *args, **kwargs) -> None:
        self.obj_type = args[0][1] if isinstance(args[0], tuple) else args[0]
        self.args = args
        self.kwargs = kwargs

    def get(self, injector: Injector):
        """Gets an instance of the object"""
        if "__init__" in self.obj_type.__dict__:
            dependencies = {}
            for name, value in self.annotations(injector):
                if name not in self.kwargs:
                    dependencies[name] = value

            instance = self.obj_type(*self.args[1:], **dependencies, **self.kwargs)
        else:
            instance = self.obj_type()
            for name, value in self.annotations(injector):
                if name not in self.kwargs:
                    setattr(instance, name, value)
                else:
                    setattr(instance, name, self.kwargs[name])

        return instance

    def annotations(self, injector):
        def toinstance(obj_type, injector: Injector):
            instance = injector.get_scoped(obj_type)
            if instance is None:
                instance = injector.get_singleton(obj_type)
            return instance

        if "__annotations__" in self.obj_type.__dict__:

            for key, value in self.obj_type.__annotations__.items():
                yield (key, toinstance(value, injector))


_global = Injector()


def add_scoped(*args, **kwargs):
    _global.add_scoped(*args, **kwargs)


def add_singleton(*args, **kwargs):
    _global.add_singleton(*args, **kwargs)


def get_scoped(*args, **kwargs):
    return _global.get_scoped(*args, **kwargs)


def get_singleton(*args, **kwargs):
    return _global.get_singleton(*args, **kwargs)


def get(*args, **kwargs):
    return _global.get(*args, **kwargs)


def clear():
    _global.clear()


def inject(func, injector=None):

    if injector is None:
        injector = _global

    instances = {}
    for name, value in func.__annotations__.items():
        if name != "return":
            instances[name] = injector.get(value)

    def injected_func(*args, **kwargs):
        return func(*args, **instances, **kwargs)

    return injected_func


class InjectorError(Exception):
    pass
