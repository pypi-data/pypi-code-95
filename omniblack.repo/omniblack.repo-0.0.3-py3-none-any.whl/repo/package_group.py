class Applier:
    def __get__(self, obj, objtype=None):
        return BoundApplier(obj)


class BoundApplier:
    def __init__(self, group):
        self.__group = group

    def __getattr__(self, name):
        return BoundFunc(name, self.__group)


class BoundFunc:
    def __init__(self, name, group):
        self.__name = name
        self.__group = group

    def __call__(self, *args, **kwargs):
        methods = (
            getattr(pkg, self.__name)
            for pkg in self.__group
        )

        return PackageGroup(
            method(*args, **kwargs)
            for method in methods
        )


class PackageGroup(list):
    apply = Applier()

    def filter(self, predicate):
        return self.__class__(
            pkg
            for pkg in self
            if predicate(pkg)
        )
