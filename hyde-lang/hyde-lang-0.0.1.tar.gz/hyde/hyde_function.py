from hyde.environment import Environment
from hyde.errors import Return
from hyde.hyde_callable import HydeCallable


class HydeFunction(HydeCallable):
    def __init__(self, declaration, closure, is_initializer = False):
        self.declaration    = declaration
        self.closure        = closure
        self.is_initializer = is_initializer

        # Override from base HydeCallable
        self.arity = len(declaration.params)

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define('this', instance)

        return HydeFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme,
                               arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, 'this')

            return return_value.value

    def __str__(self):
        return f'<fn {self.declaration.name.lexeme}>'