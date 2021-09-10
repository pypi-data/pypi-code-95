class BaseModel:
    """
    Class base for all models.
    For using the factoryModel yor class have to extends this class

    Important
    ---------
    Always init all attributes

    """
    _PREFIX_PATH = ""

    def get_prefix(self) -> str:
        return self._PREFIX_PATH

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)

