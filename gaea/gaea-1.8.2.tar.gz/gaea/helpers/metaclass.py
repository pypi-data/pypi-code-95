from gaea.errors import NotInitialized, AlreadyInitialized


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls.instances[cls] = instance
        return cls._instances[cls]


class Box:
    def __init__(self):
        self.store = None

    def __get__(self, obj, type=None):
        if self.store is None:
            raise NotInitialized()
        return self.store

    def __set__(self, obj, value):
        if self.store is not None:
            if not self.store == value:
                raise AlreadyInitialized()
            return
        self.store = value

    def __delete__(self, obj):
        self.store = None
