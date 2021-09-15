import abc

import rich


class LintRule(abc.ABC):

    def __init__(self, model):
        self.model = model

    @abc.abstractmethod
    def check(self, model):
        pass

    def __str__(self):
        return self.__class__.__name__

    def run(self):
        try:
            result = self.check(model = self.model)
            if result == True:
                rich.print(f'   :white_check_mark: {self}')
            else:
                rich.print(f'   :cross_mark: {self}')
        except Exception:
            rich.print(f'   :exclamation: {self} error: {str(err)}')