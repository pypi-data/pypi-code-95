import os
from abc import ABC, abstractmethod

import papermill as pm
import scrapbook as sb
from papermill import PapermillExecutionError

from magnumapi.optimization.constants import ERROR_KEY


class ModelExecutor(ABC):
    """An abstract class for model executor used in optimization

    """
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
