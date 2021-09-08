import sys
import importlib

def main():
    '''
    Executes a matlab function.

    The description of the function and the arguments should come from the command line arguments.
    arg[1] = package name of the compiled matlab module
    arg[2] = the name of the function
    arg[3:] = [the arguments to pass to the function]
    '''

    if len(sys.argv) >= 3:
        library_name = sys.argv[1]
        function_name = sys.argv[2]
        arguments = sys.argv[3:]

        print('Calling matlab function. Library=%s, function=%s, arguments=%s' % (library_name, function_name, arguments))

        lib = importlib.import_module(library_name)
        handle = lib.initialize()
        matlab_func = getattr(handle, function_name)
        matlab_func(*arguments, nargout=0)

        handle.terminate()
    else:
        raise ValueError('Invalid matlab function call!')

if __name__ == '__main__':
    main()