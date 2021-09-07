class CPP:
    @staticmethod
    def __protection_exception(prop):
        raise Exception(f'Can not modify constant property: {prop}')

    @staticmethod
    def protect(obj, prop):
        setattr(obj.__class__, prop, property(
            lambda self: getattr(self, '_'+prop),
            lambda self, value: CPP.__protection_exception(prop)
        ))