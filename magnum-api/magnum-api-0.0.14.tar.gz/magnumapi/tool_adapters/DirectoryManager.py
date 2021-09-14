import os
from distutils.dir_util import copy_tree
from typing import List

from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig


class DirectoryManager:
    """ A DirectoryManager class providing basic functionalities of checking file presence, creating directories, etc.

    """

    @staticmethod
    def check_if_file_exists(file_path: str) -> None:
        """Static method checking whether a file exists. If not, then a FileNotFoundError is raised.

        :param file_path: a path to a file whose presence is verified.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError('The file %s does not exist!' % file_path)

    @staticmethod
    def create_directory_if_nonexistent(output_dir: str) -> None:
        """ Static method checking whether a directory exists, if not then it is created

        :param output_dir: a path to an output directory
        """
        is_dir = os.path.isdir(output_dir)
        if not is_dir:
            os.mkdir(output_dir)

    @staticmethod
    def find_output_subdirectory_name(output_dir: str) -> str:
        """ Method finding an output subdirectory index by searching the maximum index present in an output directory
        and incrementing that index.

        :param output_dir: a path to a root output directory
        :return: a name of an output subdirectory corresponding to the incremented index
        """
        current_output_folder = '1'
        int_folder_names = [int(name) for name in os.listdir(output_dir) if name.isnumeric()]
        if int_folder_names:
            max_folder_name = max(int_folder_names)
            current_output_folder = str(max_folder_name + 1)

        return current_output_folder

    @classmethod
    def create_output_subdirectory(cls, output_dir: str, subdirectory_name: str) -> None:
        """ Static method creating an output subdirectory

        :param output_dir:
        :param subdirectory_name:
        """
        output_subdirectory_dir = os.path.join(output_dir, subdirectory_name)
        cls.create_directory_if_nonexistent(output_subdirectory_dir)

    @classmethod
    def copy_notebook_folders(cls,
                              input_folder: str,
                              notebook_configs: List[OptimizationNotebookConfig],
                              output_subdirectory_dir) -> None:
        """ Static method copying folders containing notebooks from the source directory to the output subdirectory

        :param input_folder: a root input folder
        :param notebook_configs: a list of notebook configs
        :param output_subdirectory_dir: a path to an output subdirectory
        """
        for notebook_config in notebook_configs:
            notebook_folder = notebook_config.notebook_folder
            input_notebook_folder_dir = os.path.join(input_folder, notebook_folder)
            output_notebook_subdirectory_dir = os.path.join(output_subdirectory_dir, notebook_folder)
            cls.create_directory_if_nonexistent(output_notebook_subdirectory_dir)
            copy_tree(input_notebook_folder_dir, output_notebook_subdirectory_dir)

    @classmethod
    def copy_model_input(cls, input_folder_path: str, input_folder_name: str, output_subdirectory_dir: str) -> None:
        """ Static method copying a model input from an input directory to an output subdirectory

        :param input_folder_path:
        :param input_folder_name:
        :param output_subdirectory_dir:
        """
        # ToDo: should be renamed to better denote the purpose
        ref_input_folder = os.path.join(input_folder_path, input_folder_name)
        new_input_folder = os.path.join(output_subdirectory_dir, input_folder_name)

        cls.create_directory_if_nonexistent(new_input_folder)
        copy_tree(ref_input_folder, new_input_folder)
