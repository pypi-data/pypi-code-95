from dataclasses import dataclass
from typing import List
import json

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

    @staticmethod
    def initialize_config(json_path: str) -> "OptimizationConfig":
        """ Static method initializing an optimization config from a json file

        :param json_path: a path to a json file with config
        :return: initialized OptimizationConfig instance
        """
        with open(json_path) as f:
            data = json.load(f)

        input_folder = data['input_folder']
        output_folder = data['output_folder']
        logger_rel_path = data['logger_rel_path']
        n_pop = data['n_pop']
        n_gen = data['n_gen']
        r_cross = data['r_cross']
        r_mut = data['r_mut']
        objectives = [ObjectiveConfig(**ff) for ff in data['objectives']]
        notebooks = [OptimizationNotebookConfig(**nb) for nb in data['notebooks']]

        return OptimizationConfig(input_folder=input_folder,
                                  output_folder=output_folder,
                                  logger_rel_path=logger_rel_path,
                                  n_pop=n_pop,
                                  n_gen=n_gen,
                                  r_cross=r_cross,
                                  r_mut=r_mut,
                                  objectives=objectives,
                                  notebooks=notebooks)

    def get_weight(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding weight.

        :param objective: name of an objective variable
        :return: value of the objective weight
        """
        for config_objective in self.objectives:
            if config_objective.objective == objective:
                return config_objective.weight
        raise KeyError('Objective name %s not present in objective configs.' % objective)

    def get_constraint(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding constraint.

        :param objective: name of an objective variable
        :return: value of the objective constraint
        """
        for config_objective in self.objectives:
            if config_objective.objective == objective:
                return config_objective.constraint
        raise KeyError('Objective name %s not present in objective configs.' % objective)
