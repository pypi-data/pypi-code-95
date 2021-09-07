import importlib.util
from directoryhandler import DirectoryHandler
import sys, inspect

def get_classes(module):
    classes = {}
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            classes.update({name.lower(): obj})
    return classes

class DynamicImporter:
    def __init__(self, directory_handler=DirectoryHandler()):
        self.dh = directory_handler

    def import_from_file(self, file):
        file = self.__verify_is_python_file(file)
        spec = importlib.util.spec_from_file_location(file.name, file.path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return get_classes(module)

    def import_all_from_directory(self, dir_path="", file_paths=""):
        imported_classes = {}
        if not file_paths and not dir_path:
            print("Dynamic Importer needs file paths to eat!")
            return

        elif dir_path:
            file_paths = self.dh.find_dir_via_path(dir_path).files

        for file in file_paths:
            file = self.__verify_is_python_file(file)
            if file:
                imported_classes.update(self.import_from_file(file))
        return imported_classes

    def __verify_is_python_file(self, file):
        # Convert to file object if is file path
        if isinstance(file, str):
            file = self.dh.find_files_by_name(file, return_first_found=True)
        if file.ext == "py":
            return file
        return None


if __name__ == "__main__":
    print(DynamicImporter().import_all_from_directory("Processes"))