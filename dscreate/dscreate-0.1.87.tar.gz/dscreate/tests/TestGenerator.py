import pickle
import types

from .BaseTest import BaseTest

class TestGenerator(BaseTest):
    """
    If a saved test is a class, TestGenerator reconstructs the class from
    serialized json. This generator only reconstructs the methods of the original class.
    """
    def __init__(self, data, *args):
        """
        Adds all saved methods from the test object as attributes, and runs 
        the original objects __init__ method.
        """
        for function in data['functions']:
            serialized = data['functions'][function]
            loaded_function = types.FunctionType(pickle.loads(serialized), globals())
            if function == '__init__':
                loaded_function(self, *args)
            else:
                setattr(self, function, loaded_function)

    def main(self):
        """
        Loops over attributes and runs methods that begin with the word `test`.
        """
        for item in self.__dir__():
            if 'test' in item:
                function = self.__getattribute__(item)
                if 'output' in function.__code__.co_varnames:
                    self.print_results(item, function,
                                      main=True, output=True)
                else:
                    self.print_results(item, function,
                                       main=True, output=False)