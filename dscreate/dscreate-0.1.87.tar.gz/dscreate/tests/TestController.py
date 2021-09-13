import os
import types
import pickle
from IPython.display import display, Markdown

from .BaseTest import BaseTest
from .TestGenerator import TestGenerator


class Tests(BaseTest):
    """
    Controller object for saving and running tests.
    """
    def __init__(self):
        # If a folder for solution objects has not been created
        # it is created here
        if not os.path.isdir('.solution_files'):
            os.mkdir('.solution_files')
        self.test_dir = os.path.join('.solution_files', '.test_obj')
        if not os.path.isdir(self.test_dir):
            os.mkdir(self.test_dir)
            
    def save(self, callable, name, assertion=True):
        """
        Saves a callable function or class object to disk.

        Arguments
        ---------

        callable:      A function or class object.
        name:          String. The name of the test. This argument will be used to run the 
                       the test, and should be representative of what the test is check.

        assertion:     Boolean. Default: True. 
                       When passing in a function object, if assertion=True
                       The function should either return True or False
                       If you would like to return a custom message for the test
                       assertion should be set to False.

        Returns
        -------
        None
        """
        # To run saved callable objects, the objects must be serialized
        # and saved to json. 
        # The json is structured as follows:
              # {'assertion': <boolean>,
              #  'kind': <string either "function" or "class">,
              #  'functions': <function object if kind="string"
              #                 else {"name of class method": function object}}
        data = {}
        data['assertion'] = assertion
        # source: https://stackoverflow.com/a/29250620
        if isinstance(callable, types.FunctionType):
            data['kind'] = 'function'
            callable_ = pickle.dumps(callable.__code__)
            data['functions'] = callable_
        elif isinstance(callable, type):
            data['kind'] = 'class' 
            data['functions'] = {}
            for item in callable.__dict__:
                if isinstance(callable.__dict__[item], types.FunctionType):
                    serialized = pickle.dumps(callable.__dict__[item].__code__)
                    data['functions'][item] = serialized
        path = os.path.join(self.test_dir, name.strip().lower() + '.pkl')
        file = open(path, 'wb')
        pickle.dump(data, file)
        file.close()

    def run(self, name, *args):
        """
        Runs a saved test. 

        Arguments
        ---------
        name:       The name of the test. This is the string that was used
                    to save the test object.

        *args:      This is typically the answer that is being tested. Multiple
                    arguments are allowed.

        Returns
        -------
        A print out for each test.
        """
        path = os.path.join(self.test_dir, name.strip().lower() + '.pkl')
        file = open(path, 'rb')
        data = pickle.load(file)
        file.close()
        
        if data['kind'] == 'function' and data['assertion']:
            function = types.FunctionType(pickle.loads(data['functions']), globals())
            self.print_results(name, function, *args)
            
        elif data['kind'] == 'function':
            function = types.FunctionType(pickle.loads(data['functions']), globals())
            output = function(*args)
            markdown = Markdown(f"""**{name}:** {output}""")
            display(markdown)
        
        elif data['kind'] == 'class':
            generator = TestGenerator(data, *args)
            generator.main()