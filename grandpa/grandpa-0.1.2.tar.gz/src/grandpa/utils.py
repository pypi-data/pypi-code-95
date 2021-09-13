import inspect
import os


def do_import(class_path: str):
    """
    Imports a class from a string. Modules can either be separated by a '.' or a '/'.
    Example: class_path = data_processing/dp_trees/tree/Tree will import the tree class.

    Args:
        class_path: Path to import

    Returns:
        The imported class
    """
    class_path = class_path.replace('/', '.')
    module, import_class = class_path.rsplit('.', 1)
    return getattr(__import__(module, fromlist=[import_class]), import_class)


def filter_kwargs(func, kwargs):
    filtered_call_params = {}
    for k, v in kwargs.items():
        if k in inspect.signature(func).parameters or any(str(p.kind) == 'VAR_KEYWORD' for p in
                                                          inspect.signature(func).parameters.values()):
            filtered_call_params[k] = v
    return filtered_call_params


def print_warning(txt: str):
    """
    Prints a warning in the color yellow to the console.

    Args:
        txt: String to print.

    Returns:
        None
    """
    print("\033[93m WARNING: " + txt + '\033[0m')


def check_debug():
    return os.getenv("project_x_debug") == "true"
