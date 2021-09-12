from django.core.cache import cache
from .list import normalize_list


class CacheManager():
    __instance__ = None
    default_populate_values = {}

    def __init__(self):
        if CacheManager.__instance__ is None:
            super().__init__()
            CacheManager.__instance__ = self
        else:
            raise ValueError("You cannot create another CacheManager class")

    @ staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not CacheManager.__instance__:
            CacheManager()
        return CacheManager.__instance__

    def add_default_population_value(self, value_name, populate_function, param_values=[]):
        param_values = normalize_list(param_values)

        self.default_populate_values[value_name] = {
            "function": populate_function, "param_values": param_values}

        self.populate_value(value_name)

    def reset_default_values(self):
        self.default_populate_values = {}

    def reset_cache(self):
        cache.clear()
        self.populate_values()

    def full_reset(self):
        self.reset_default_values()
        self.reset_cache()

    def populate_value(self, value_name):
        if value_name not in self.default_populate_values:
            raise ValueError(f'{value_name} is not a managed cache value')
        else:
            managed_cache_value = self.default_populate_values[value_name]

            param_values = managed_cache_value['param_values']
            populate_function = managed_cache_value['function']

            if(len(param_values) == 0):
                self.set(value_name, populate_function())
            else:
                self.set(value_name, populate_function(*param_values))

    def populate_values(self):
        for value_name in self.default_populate_values:
            self.populate_value(value_name)

    def set(self, value_name, value):
        cache.set(value_name.replace(" ", '-'), value)

    def get(self, value_name):
        return cache.get(value_name.replace(" ", '-'))

    def set_or_get(self, value_name, default_value):
        if self.get(value_name) == None:
            self.set(value_name, default_value)

        return self.get(value_name)
