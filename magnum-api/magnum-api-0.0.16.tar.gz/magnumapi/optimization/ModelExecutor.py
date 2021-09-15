import os
from abc import ABC, abstractmethod

import papermill as pm
import scrapbook as sb
from papermill import PapermillExecutionError

from magnumapi.optimization import NotebookConverter
from magnumapi.optimization.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.constants import ERROR_KEY
from magnumapi.tool_adapters.DirectoryManager import DirectoryManager


class ModelExecutor(ABC):
    """An abstract class for model executor used in optimization

    """

    @staticmethod
    def initialize_folder_structure(config: OptimizationConfig) -> str:
        """ Method initializing the folder directory structure to store optimization results outside of the main
        directory.

        :return: a path to the output root directory where all results are stored.
        """
        DirectoryManager.create_directory_if_nonexistent(config.output_folder)
        subdirectory_name = DirectoryManager.find_output_subdirectory_name(config.output_folder)
        output_subdirectory_dir = os.path.join(config.output_folder, subdirectory_name)

        DirectoryManager.create_directory_if_nonexistent(output_subdirectory_dir)
        DirectoryManager.copy_model_input(config.input_folder, 'input', output_subdirectory_dir)
        DirectoryManager.copy_notebook_folders(config.input_folder, config.notebooks, output_subdirectory_dir)
        DirectoryManager.create_directory_if_nonexistent(os.path.join(output_subdirectory_dir, 'optimization'))
        DirectoryManager.copy_model_input(config.input_folder, 'optimization', output_subdirectory_dir)

        logger_path = os.path.join(output_subdirectory_dir, config.logger_rel_path)
        print('The logger is saved in: %s' % logger_path)

        for config_notebook in config.notebooks:
            input_ipynb_file_path = os.path.join(output_subdirectory_dir,
                                                 config_notebook.notebook_folder,
                                                 config_notebook.notebook_name)
            output_ipynb_file_path = os.path.join(output_subdirectory_dir,
                                                  config_notebook.notebook_folder,
                                                  config_notebook.notebook_name.lower().replace('.ipynb', '.py'))
            NotebookConverter.convert_notebook_to_script(input_ipynb_file_path,
                                                         config_notebook.notebook_name.lower().split('.')[0],
                                                         output_ipynb_file_path)

        return output_subdirectory_dir

    @abstractmethod
    def execute(self, model_dir: str, model_name: str, parameters_dct: dict) -> dict:
        """Method executing a model and returning figures of merit.

        :param model_dir: model directory
        :param model_name: name of a model
        :param parameters_dct: a dictionary with model execution parameters and corresponding values

        :return: a dictionary with figures of merit if the computation was successful, otherwise an empty dictionary
        """
        raise NotImplementedError('This method is not implemented for this class')


class ScriptModelExecutor(ModelExecutor):
    """ An implementation of ModelExecutor abstract class for scripts

    """

    def execute(self, model_dir: str, model_name: str, parameters_dct: dict) -> dict:
        """Method calculating figures of merit with scripts. Notebooks are converted to scripts.

        :param model_dir: model directory
        :param model_name: name of a model
        :param parameters_dct: a dictionary with model execution parameters and corresponding values

        :return: a dictionary with figures of merit if the computation was successful, otherwise a dictionary with -1
        error code is returned.
        """
        notebook_name = model_name.split('.')[0].lower()
        cwd = os.getcwd()

        os.chdir(model_dir)
        run = getattr(__import__(notebook_name), 'run_' + notebook_name)
        print('Running %s script' % notebook_name)
        try:
            fom_model = run(**parameters_dct)
        except Exception as exception:
            print(exception)
            return {ERROR_KEY: -1}
        os.chdir(cwd)

        return fom_model


class NotebookModelExecutor(ModelExecutor):
    """ An implementation of ModelExecutor abstract class for notebooks

    """
    def execute(self, model_dir: str, model_name: str, parameters_dct: dict) -> dict:
        """Method calculating figures of merit with notebooks (papermill and scrapbook packages).

        :return: a dictionary with figures of merit if the computation was successful, otherwise a dictionary with -1
        error code is returned.
        """
        notebook_path = os.path.join(model_dir, model_name)
        notebook_name_split = model_name.split('.')
        out_notebook_name = '%s_out.%s' % tuple(notebook_name_split)

        out_notebook_path = os.path.join(model_dir, out_notebook_name)

        try:
            pm.execute_notebook(notebook_path, out_notebook_path, cwd=model_dir, parameters=parameters_dct)
        except PapermillExecutionError as e:
            # on error print the message
            print(e.exec_count)
            print(e.source)
            print(e.traceback[-1])
            return {ERROR_KEY: -1}
        except Exception as exception:
            raise Exception(exception)

        # fetch figure of merit
        return sb.read_notebook(out_notebook_path).scraps['model_results'].data


class ModelExecutorFactory:
    """ A factory class returning either a script or notebook executor

    """
    @staticmethod
    def build(is_script_executed: bool) -> "ModelExecutor":
        """

        :param is_script_executed: True if notebooks are executed as script, False otherwise
        :return: ScriptModelExecutor instance if True, otherwise NotebookModelExecutor
        """
        if is_script_executed:
            return ScriptModelExecutor()
        else:
            return NotebookModelExecutor()
