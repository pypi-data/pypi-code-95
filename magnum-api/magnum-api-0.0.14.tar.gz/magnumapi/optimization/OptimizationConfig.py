from dataclasses import dataclass
from typing import List

from magnumapi.optimization.ObjectiveConfig import ObjectiveConfig
from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig


@dataclass
class OptimizationConfig:
    """Class for optimization config used for the genetic algorithm.

    Attributes:
       input_folder (str): The path to an input folder
       output_folder (float): The path to an output folder
       logger_rel_path (float): The path to the logger csv file
       n_pop (int): The number of individuals, i.e., the population size
       n_gen (int): The number of generations
       r_cross (float): The probability of crossover
       r_mut (float): The probability of mutation
       objectives (list): The list of objective configs
       notebooks (list): The list of notebook configs
    """
    input_folder: str
    output_folder: str
    logger_rel_path: str
    n_pop: int
    n_gen: int
    r_cross: float
    r_mut: float
    objectives: List[ObjectiveConfig]
    notebooks: List[OptimizationNotebookConfig]

    def __str__(self) -> str:
        notebooks_str = "\n\n".join(str(notebook) for notebook in self.notebooks)
        objectives_str = "\n\n".join(str(objective) for objective in self.objectives)
        return "input_folder: %s\n" \
               "output_folder: %s\n" \
               "logger_rel_path: %s\n" \
               "n_pop: %d\n" \
               "n_gen: %d\n" \
               "r_cross: %f\n" \
               "r_mut: %f\n" \
               "objectives: \n\n" \
               "%snotebooks: \n\n" \
               "%s" % (self.input_folder,
                       self.output_folder,
                       self.logger_rel_path,
                       self.n_pop,
                       self.n_gen,
                       self.r_cross,
                       self.r_mut,
                       objectives_str,
                       notebooks_str)
