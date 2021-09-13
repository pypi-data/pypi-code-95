import types
from pathlib import Path

module_without_unit_test = {
    "geoformat/conf/decorator.py",
    "geoformat/conf/driver_variable.py",
    "geoformat/conf/error_messages.py",
    "geoformat/conf/fields_variable.py",
    "geoformat/conf/geometry_variable.py",
    "geoformat/conf/timer.py",
    "geoformat/db/db_request.py",
    "geoformat/driver/ogr/ogr_driver.py",
    "geoformat/explore_data/random_geometry.py"
}

deprecated_function = {'clause_where_combination'}


def iterate_over_directory_in_geoformat_module(p):
    # get dir
    dir_list = [x for x in p.iterdir() if x.is_dir() and x.name != '__pycache__']

    if dir_list:
        for dir in dir_list:
            dir_list += iterate_over_directory_in_geoformat_module(p=dir)

    return dir_list


def get_relative_path(path, origin_path):
    return '/'.join(path.parts[len(origin_path.parts):])


class GeoformatInspector:

    def __init__(self, path='None'):
        self.geoformat_root_path = Path(__file__).parent.parent.parent.joinpath()
        self.geoformat_lib_dir_path = self.geoformat_root_path.joinpath('geoformat')
        self.tests_dir_path = self.geoformat_root_path.joinpath('tests')
        self.tests_geoformat_lib_dir = self.geoformat_root_path.joinpath('tests/geoformat')

    def check_tests_structure(self):
        dir_list = iterate_over_directory_in_geoformat_module(p=self.geoformat_lib_dir_path)

        for dir_path in dir_list:
            relative_dir_part = get_relative_path(path=dir_path, origin_path=self.geoformat_lib_dir_path)
            relativ_part_path = Path(relative_dir_part)
            test_geoformat_lib_dir_path = self.tests_geoformat_lib_dir.joinpath(relativ_part_path)
            if test_geoformat_lib_dir_path.is_dir() is False:
                print('tests dir {} missing !'.format(relativ_part_path))

    def get_objects_in_geoformat_module(self, geoformat_module_import_path, from_list=None, object_type=None):

        if from_list is None:
            from_list = [None]
        function_set = set()

        try:
            module = __import__(
                name=geoformat_module_import_path,
                locals=None,
                globals=None,
                fromlist=from_list,
                level=0
            )

            for str_obj in dir(module):
                if not str_obj.startswith('_'):  # exclude function that start to '_'
                    obj = getattr(module, str_obj)

                    write_str_obj = True
                    if object_type:
                        if not isinstance(obj, object_type):
                            write_str_obj = False
                    if write_str_obj is True:
                        function_set.update({str_obj})

        except ModuleNotFoundError:
            parts_path = geoformat_module_import_path.split('.')
            file_path = Path(*parts_path)
            print('tests files {} missing'.format(file_path))

        return function_set

    def check_tests_function(self):
        dir_list = iterate_over_directory_in_geoformat_module(p=self.geoformat_lib_dir_path)
        geoformat_function_to_test_set = set()
        geoformat_tested_function_set = set()
        for dir_path in dir_list:
            py_path_list = [path for path in dir_path.glob('*.py') if path.name != "__init__.py"]
            if py_path_list:
                for py_path in py_path_list:
                    relative_path_to_py_path_from_root_path = get_relative_path(path=py_path, origin_path=self.geoformat_root_path)
                    # if path is not in module_without_unit_test
                    if relative_path_to_py_path_from_root_path not in module_without_unit_test:

                        relative_py_path = Path(relative_path_to_py_path_from_root_path)

                        # get geoformat functions
                        relative_geoformat_lib_py_path_str_for_import = '.'.join(relative_py_path.parts).replace('.py', '')
                        geoformat_function_to_test_set.update(
                            self.get_objects_in_geoformat_module(
                                geoformat_module_import_path=relative_geoformat_lib_py_path_str_for_import,
                                from_list=['object'],
                                object_type=types.FunctionType
                            )
                        )

                        # get tests functions
                        relative_tests_py_path = Path('tests').joinpath(relative_py_path)
                        relative_tests_py_path_parts = list(relative_tests_py_path.parts)
                        relative_tests_py_path_parts[-1] = 'test_' + relative_tests_py_path_parts[-1]
                        relative_tests_py_path_str_for_import = '.'.join(relative_tests_py_path_parts).replace('.py', '')
                        geoformat_tested_function_set.update(
                            self.get_objects_in_geoformat_module(
                                geoformat_module_import_path=relative_tests_py_path_str_for_import,
                                object_type=dict
                            )
                        )

        # filter and only get variable with suffix
        suffix = '_parameters'
        # recreate original name with test function name
        geoformat_tested_function_set = {suffix.join(value.split(suffix)[:-1]) for value in geoformat_tested_function_set if value.endswith(suffix)}
        # make difference to get only not tested function
        not_tested_function_set = geoformat_function_to_test_set - geoformat_tested_function_set
        if not_tested_function_set:
            for not_tested_function_name in not_tested_function_set:
                if not_tested_function_name not in deprecated_function:
                    print('function :', not_tested_function_name, 'must be tested')


if __name__ == '__main__':
    inspector = GeoformatInspector()

    # check tests
    inspector.check_tests_structure()
    inspector.check_tests_function()

    # TODO check if function are in geoformat.__init__
    # TODO check if tested function are in test_all
