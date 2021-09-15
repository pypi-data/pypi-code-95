from threading import Timer
from typing import List, Dict

import pandas as pd
from IPython.display import display

from magnumapi.geometry.roxie.CableDatabase import CableDatabase
from magnumapi.optimization.GeneticOptimization import RoxieGeneticOptimization
from magnumapi.optimization.Logger import Logger
from magnumapi.optimization.OptimizationCockpitWidget import OptimizationCockpitWidget
from magnumapi.optimization.OptimizationConfig import OptimizationConfig


class RepeatedTimer(object):
    """ Class providing a repeated timer functionality used for updating the optimization cockpit

    """
    def __init__(self, interval: float, function, *args, **kwargs) -> None:
        """ Constructor of a RepeatedTimer instance

        :param interval: interval of function execution (in seconds)
        :param function: function to be executed at regular intervals
        :param args: list of arguments for the function
        :param kwargs: list of keyword-arguments for the function
        """
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class OptimizationCockpit:
    """ Class displaying and refreshing the optimization cockpit.

    """

    def __init__(self,
                 gen_opt: RoxieGeneticOptimization,
                 logger_abs_path: str,
                 config: OptimizationConfig,
                 optim_input_df: pd.DataFrame,
                 block_inputs: List[Dict],
                 cadata: CableDatabase) -> None:
        """ Constructor of the OptimizationCockpit class

        :param logger_abs_path: an absolute path to the logger
        :param config: optimization config instance
        :param optim_input_df: a dataframe with optimization objectives
        :param block_inputs: a list of block definitions of a coil
        :param cadata: a CableDatabase instance
        """
        self.gen_opt = gen_opt
        self.logger_abs_path = logger_abs_path
        self.logger_df = pd.read_csv(self.logger_abs_path, index_col=0)
        self.config = config
        self.optim_input_df = optim_input_df
        self.block_inputs = block_inputs
        self.cadata = cadata
        self.widget = None

    def display(self, t_sleep_in_sec=5.0) -> None:
        """ Method displaying the cockpit and starting a timer to refresh the cockpit with a given period.

        :param t_sleep_in_sec: the refresh interval for the cockpit
        """
        if len(self.logger_df):
            self.widget = OptimizationCockpitWidget(self.gen_opt,
                                                    self.config,
                                                    self.optim_input_df,
                                                    self.cadata)

            self.widget.build()
            display(self.widget.show())

            RepeatedTimer(t_sleep_in_sec, self.update_cockpit)
        else:
            raise Warning('The logger dataframe is empty, no data to display!')

    def update_cockpit(self) -> None:
        """ Method updating the cockpit by checking whether an update is available, i.e., the logger was populated with
        new information.

        """
        logger_new_df = pd.read_csv(self.logger_abs_path, index_col=0)
        if len(logger_new_df) > len(self.logger_df):
            self.logger_df = logger_new_df
            self.widget.min_logger_df = Logger.extract_min_rows_from_logger_df(self.logger_df, self.config.n_pop)
            self.widget.widget.data = []
            self.widget.build()
