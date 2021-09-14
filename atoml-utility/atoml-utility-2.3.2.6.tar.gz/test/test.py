import sys
import unittest

from general_utility import utils as us
from general_utility.appbase import ab
from plugin_utility.iplugin import iPlugin
from databar_utility.databar import Databar

class TestSequenceFunctions(unittest.TestCase):

    def test_print_current_env_information(self):
        print(ab.print_current_env_information())

    #########################################################

    def test_os_path(self):
        filename = sys.argv[0]

        print(us.get_cur_dir())
        print(us.get_parent_dir(filename))
        print(us.get_dir_from_filepath(filename))
        print(us.get_path_suffix_from_filepath(filename))
        print(us.get_name_suffix_from_filepath(filename))
        print(us.get_suffix_from_filepath(filename))
        print(us.getfiletime(filename))
        print(us.get_path_name_suffix_from_filepath(filename))

    def test_dict_list_str(self):
        params_dict = 'a=aaa,b=bbb'
        params_dict = us.str_to_dict(params_dict, ',', '=')
        print(params_dict)

        params = {'a':'${a}', 'b':'${b}', 'c':'${c}'}

        print(us.dict_place(params, params_dict))

        print(us.dict_merged(params, params_dict))
        
        for key, value in params.items():
            params[key] = us.item_place(value, params_dict)
        print(params)

    def test_load_databar(self):
        databar = Databar(protocol_version = '2.2', input = 'test')


if __name__ == '__main__':
    unittest.main()