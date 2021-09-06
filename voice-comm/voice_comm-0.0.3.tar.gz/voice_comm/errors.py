class ModuleNotFound(Exception):
    def __init__(self, name):
        self.fmt = f'Modulen {name} could not be loaded.'

    def __str__(self):
        return self.fmt

class ModuleAlreadyLoaded(Exception):
    def __init__(self, name):
        self.fmt = f'Module {name} already laoded.'

    def __str__(self):
        return self.fmt

class ModuleFailed(Exception):
    def __init__(self, name, e):
        self.fmt = f'Module {name} failed, because {e}'

    def __str__(self):
        return self.fmt