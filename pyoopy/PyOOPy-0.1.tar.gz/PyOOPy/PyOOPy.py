import inspect


class PyOOPy:
    class Protected:
        pass

    class Private:
        pass

    class Public:
        pass

    class AccessError(AttributeError):
        def __init__(self, cls_name, attr_name):
            msg = f"Attribute '{attr_name}' of object '{cls_name}' is not public"
            super().__init__(msg)

    @staticmethod
    def access_restriction(fun, self, *args, **kwargs):
        caller = inspect.currentframe().f_back.f_back.f_locals.get("self")
        if caller is not self:
            cls_name = self.__class__.__name__
            attr_name = fun.__name__
            raise PyOOPy.AccessError(cls_name, attr_name)
        return fun(self, *args, **kwargs)

    @staticmethod
    def protected(fun):
        def wrapper(self, *args, **kwargs):
            return self.access_restriction(fun, self, *args, **kwargs)

        return wrapper

    @staticmethod
    def private(fun):
        def wrapper(self, *args, **kwargs):
            return self.access_restriction(fun, self, *args, **kwargs)

        return wrapper

    @staticmethod
    def public(fun):
        return fun

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, name)

        # has to be public
        if name[0] == '_':
            return obj

        # callables differently
        if callable(obj):
            parent = self.__class__.__bases__[0]
            private_in_parent = False
            try:
                private_in_parent = getattr(parent, name).__qualname__ == 'PyOOPy.private.<locals>.wrapper'
            except AttributeError:
                pass
            if private_in_parent:
                raise PyOOPy.AccessError(self.__class__.__name__, name)
            return obj

        # not annoted
        annoted = self.__init__.__annotations__.get(name) in (PyOOPy.Private, PyOOPy.Protected)
        if not annoted:
            return obj

        # annoted but not called by owner
        caller = inspect.currentframe().f_back.f_locals.get("self")
        if caller is not self:
            raise PyOOPy.AccessError(self.__class__.__name__, name)

        # parent's private field
        parents = self.__class__.__bases__
        for parent in parents:
            if parent != PyOOPy and parent.__init__.__annotations__.get(name) is PyOOPy.Private:
                raise PyOOPy.AccessError(self.__class__.__name__, name)

        return obj
