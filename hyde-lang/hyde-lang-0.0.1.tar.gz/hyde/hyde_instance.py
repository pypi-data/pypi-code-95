from hyde.environment import Environment
from hyde.errors import BaseError


class HydeInstanceError(BaseError):
    pass


class HydeInstance:
    def __init__(self, klass):
        self.klass  = klass
        self.fields = {}
    
    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise HydeInstanceError(name, f'Undefined property {name.lexeme} for {self.klass} instance.')

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f'{self.klass.name} instance'