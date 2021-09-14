import unittest
import os, sys
import sys
sys.path.append(os.path.join(os.getcwd(), 'background'))
from plugin_utility.plugin_object import Plugin_Runner, Plugin_Object

import os
example_plugin_dir = os.path.join(os.getcwd(), './background/plugin_utility/Example')
example_plugin_config = os.path.join(example_plugin_dir, 'nasdaq100_config.json')

class TestSequenceFunctions(unittest.TestCase):

    def test_plugin(self):
        for root, dirs, _ in os.walk(example_plugin_dir):
            if (root == example_plugin_dir): # 此处只遍历一级子目录
                for dir in dirs:
                    plugin_obj = Plugin_Object(os.path.join(root, dir))
                    # if (plugin_obj is not None):
                    #     plugin_obj.test()

    # def test_Plugin_Runner(self):
    #     plugin_Runner = Plugin_Runner(example_plugin_config)
    #     plugin_Runner.test()

    #########################################################


if __name__ == '__main__':
    unittest.main()