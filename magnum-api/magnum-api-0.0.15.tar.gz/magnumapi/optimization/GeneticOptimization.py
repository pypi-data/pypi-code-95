from abc import ABC, abstractmethod
import json
import os
from shutil import copyfile
from copy import deepcopy
from typing import List, TypeVar, Tuple, Dict

import numpy as np
import pandas as pd
from IPython.display import display

from magnumapi.optimization.DesignVariable import GeneticDesignVariable
from magnumapi.optimization.Logger import Logger
from magnumapi.optimization.ModelExecutor import ModelExecutorFactory
from magnumapi.optimization.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig
from magnumapi.optimization.constants import PENALTY, ERROR_KEY

T = TypeVar('T')


class Optimization(ABC):
    def __init__(self, n_gen: int, n_pop: int, logger_rel_path='', output_subdirectory_dir=''):
        """ Constructor of a GeneticOptimization instance

        :param output_subdirectory_dir: a root subdirectory with output results
        """
        self.n_gen = n_gen
        self.n_pop = n_pop
        self.logger = Logger(output_subdirectory_dir, logger_rel_path)
        self.output_subdirectory_dir = output_subdirectory_dir

    def optimize(self) -> None:
        """ Method executing the main optimization loop of the genetic algorithm

        """
        # initial population of random chromosomes
        pop = self.initialize_population()

        # enumerate generations
        for gen in range(self.n_gen):
            print('Generation:', gen)
            # decode population
            scores = []

            for index, individual in enumerate(pop):
                print('\tIndividual:', index)
                self.update_model(individual)

                fom_dct = self.calculate_figures_of_merit(individual)
                score = self.calculate_score(fom_dct)
                scores.append(score)

                # log current computation results
                self.logger.append_to_logger(self.decode_individual(individual), fom_dct, score)

            # display an update
            print(sorted(scores))
            min_logger_df = self.get_min_fitness_per_generation()
            display(min_logger_df[min_logger_df.index == min_logger_df.index[-1]])

            # apply genetic operators of selection, crossover, and mutation
            pop = self.update_generation(pop, scores)
            self.logger.save_logger()

    @abstractmethod
    def initialize_population(self) -> List[List[int]]:
        """ Abstract method initializing a population of candidate solutions

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def update_model(self, individual: List[int]) -> None:
        """ Abstract method updating model parameters

        :param individual: a list of 0s and 1s representing a model to be optimised
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def decode_individual(self, individual: List[int]) -> Dict:
        """ Method decoding a chromosome from a list of ints (0, 1) to a dictionary containing values of each
        design variable. There is a check whether the decoded value matches the input range (the resulting value may
        exceed the range due to the application of crossover and mutation operators).

        :param individual: a list of ints (0, 1) representing an individual's chromosome
        :return: a dictionary with all design variables
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def calculate_figures_of_merit(self, individual: List[int]) -> dict:
        """ Abstract method calculating figures of merit

        :param individual: a list of 0s and 1s representing a model to be optimised
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def calculate_score(self, fom_dct: Dict[str, float]) -> float:
        """ Method calculating score from a dictionary mapping objective variable to its value.
        If any of the returned values is NaN, then the penalty value is returned.

        :param fom_dct: figure of merit dictionary mapping objective variable to its value
        :return: fitness function value obtained as weighted sum
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def update_generation(self, pop: List[List[int]], scores: List[float], k_selection=3) -> List[List[int]]:
        raise NotImplementedError('This method is not implemented for this class')

    def get_logger_df(self) -> pd.DataFrame:
        return self.logger.get_logger_df()

    def get_mean_fitness_per_generation(self) -> pd.DataFrame:
        return self.logger.get_mean_fitness_per_generation(self.n_pop)

    def get_min_fitness_per_generation(self) -> pd.DataFrame:
        return self.logger.get_min_fitness_per_generation(self.n_pop)


class GeneticOptimization(Optimization, ABC):
    """ Base GeneticOptimization class implementing a basic genetic optimization algorithm.

    """

    def __init__(self,
                 config: OptimizationConfig,
                 design_variables_df: pd.DataFrame,
                 n_elite=2,
                 output_subdirectory_dir='') -> None:
        """ Constructor of a GeneticOptimization instance

        :param config: a config for the genetic optimization
        :param design_variables_df: a dataframe with ranges of design variables
        :param n_elite: the number of individuals for elitism
        :param output_subdirectory_dir: a root subdirectory with output results
        """
        super().__init__(config.n_gen, config.n_pop, config.logger_rel_path, output_subdirectory_dir)
        self.r_cross = config.r_cross
        self.r_mut = config.r_mut
        self.config = config
        self.n_elite = n_elite
        self.design_variables = GeneticOptimization.initialize_design_variables(design_variables_df)

    @staticmethod
    def initialize_design_variables(design_variables_df: pd.DataFrame) -> List[GeneticDesignVariable]:
        """ Static method initializing design variables from a DataFrame

        :param design_variables_df: a DataFrame with design variables
        :return: a list of design variables
        """
        design_variables = []
        for index, row in design_variables_df.iterrows():
            design_variables.append(GeneticDesignVariable(**row.to_dict()))

        return design_variables

    @staticmethod
    def initialize_config(json_path: str) -> OptimizationConfig:
        return OptimizationConfig.initialize_config(json_path)

    def calculate_score(self, fom_dct: Dict[str, float]) -> float:
        """ Method calculating score from a dictionary mapping objective variable to its value.
        If any of the returned values is NaN, then the penalty value is returned.

        :param fom_dct: figure of merit dictionary mapping objective variable to its value
        :return: fitness function value obtained as weighted sum
        """
        if any([np.isnan(value) for value in fom_dct.values()]):
            return PENALTY

        score = 0
        for objective_config in self.config.objectives:
            score += objective_config.weight * (fom_dct[objective_config.objective] - objective_config.constraint)

        return score

    def update_generation(self, pop: List[List[int]], scores: List[float], k_selection=3) -> List[List[int]]:
        """ Method updating generation of individuals representing candidate solutions. The update consists of applying
        the following genetic operators:
        - application of elitism (if n_elite > 0), i.e., direct propagation of best n_elite individuals to the next
        iteration of the algorithm
        - tournament selection (with given tournament size, k_selection) of parents for mating
        - crossover of pairs of parents to produce a pair of children; crossover happens with a certain probability
        - mutation with a given probability

        :param pop: list of individuals with candidate solutions. Each candidate is represented as a bitstring
        :param scores: a list of scores corresponding to the individuals
        :param k_selection: size of the tournament for selection
        :return: a new generation of individuals after applying genetic operators to the input generation
        """
        # elitism - keep best two forward
        # # sort according to the best result
        pop_sorted = [pop_el for _, pop_el in sorted(zip(scores, pop))]
        scores_sorted = [score_el for score_el, _ in sorted(zip(scores, pop))]
        # take two from pop and scores
        elite = pop_sorted[:self.n_elite]
        # select parents
        selected = [GeneticOptimization.selection(pop_sorted, scores_sorted, k_selection)
                    for _ in range(self.n_pop - self.n_elite)]
        # create the next generation
        children = list()
        for i in range(0, self.n_pop - self.n_elite, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i + 1]
            # crossover and mutation
            for c in self.crossover(p1, p2):
                # mutation
                self.mutation(c)
                # store for next generation
                children.append(c)
        # replace population
        return elite + children

    @staticmethod
    def selection(pop: List[List[int]], scores: List[float], k=3) -> List[int]:
        """ Method selecting best individuals according to the fitness value. The algorithm starts with a randomly
        selected individual. Then, it selects k random indices. For each of the indices it updates the initially
        selected individual by comparing the fitness with k selected individuals.

        :param pop: population of individuals, a list of genomes; sorted according to the score in ascending order
        :param scores: a list of fitness function scores, one per genome; sorted according to the score in ascending
        order
        :param k: the size of the tournament selection
        :return: a selected genome
        """
        # first random selection
        selection_ix = np.random.randint(len(pop))
        for ix in np.random.randint(0, len(pop), k - 1):
            # check if better (e.g. perform a tournament)
            if scores[ix] < scores[selection_ix]:
                selection_ix = ix

        return pop[selection_ix]

    def crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """ Method performing a single cross-over operation between two parents and creates two children. The cross-over
        point is selected at random.

        :param parent1: first parent
        :param parent2: second parent
        :return: a tuple with two children
        """
        # children are copies of parents by default
        child1, child2 = parent1.copy(), parent2.copy()
        # check for recombination
        if np.random.rand() < self.r_cross:
            # select crossover point that is not on the end of the string
            idx_crossover = np.random.randint(1, len(parent1) - 2)
            # perform crossover
            child1 = parent1[:idx_crossover] + parent2[idx_crossover:]
            child2 = parent2[:idx_crossover] + parent1[idx_crossover:]
        return child1, child2

    def mutation(self, bitstring: List[int]) -> List[int]:
        """ Method performing a bit-flip mutation with a certain probability

        :param bitstring: input bitstring for which the mutation is performed
        :return: updated bitstring
        """
        output_bitstring = bitstring.copy()
        for i in range(len(bitstring)):
            # check for a mutation
            if np.random.rand() < self.r_mut:
                # flip the bit
                output_bitstring[i] = 1 - output_bitstring[i]

        return output_bitstring


class RoxieGeneticOptimization(GeneticOptimization):
    """ A RoxieGeneticOptimization class implementing a basic genetic optimization algorithm. The class contains methods
    for updating a ROXIE input according to the update from the genetic algorithm.

    """

    def __init__(self,
                 config: OptimizationConfig,
                 design_variables_df: pd.DataFrame,
                 block_inputs: List[Dict],
                 model_input_path: str = '',
                 is_script_executed: bool = True,
                 n_elite=2,
                 output_subdirectory_dir: str = '') -> None:
        """ Constructor of a RoxieGeneticOptimization instance

        :param config: a config for the genetic optimization
        :param design_variables_df: a dataframe with ranges of design variables
        :param block_inputs: input block inputs to be updated; it is a list of dictionaries
        :param model_input_path: a path to a model input json file
        :param is_script_executed: True if notebooks are executed as script, False otherwise
        :param n_elite: the number of individuals for elitism
        :param output_subdirectory_dir: a root subdirectory with output results
        """
        super().__init__(config, design_variables_df, n_elite, output_subdirectory_dir)
        self.block_inputs = block_inputs
        self.model_input_path = model_input_path
        self.is_script_executed = is_script_executed

    def initialize_population(self) -> List[List[int]]:
        pop = []
        for _ in range(self.n_pop):
            chromosome = RoxieGeneticOptimization.generate_random_chromosome(self.design_variables)
            pop.append(chromosome)
        return pop

    @staticmethod
    def generate_random_chromosome(design_variables: List[GeneticDesignVariable]) -> List[int]:
        """ Static method generating a random chromosome representing an individual based on input information.

        :param design_variables: a list with definition of design variables
        :return: a randomly generated chromosome as a list of ints (0, 1)
        """
        chromosome = []
        for design_variable in design_variables:
            chromosome.extend(design_variable.generate_random_gene())

        return chromosome

    def update_model(self, individual: List[int]) -> None:
        # decoded_chromosome: a chromosome decoded into a dictionary with keys corresponding to parameter names
        # (variable and block index) mapping to parameter values
        decoded_chromosome = self.decode_individual(individual)
        updated_block_inputs = self.update_model_parameters(decoded_chromosome)

        # write updated input to json
        with open(self.model_input_path, 'w') as file:
            json.dump(updated_block_inputs, file, sort_keys=True, indent=4)

    def decode_individual(self, individual: List[int]) -> Dict:
        block_variable_value = {}
        for index, design_variable in enumerate(self.design_variables):
            # extract gene
            sum_bits = sum([dv.bits for dv in self.design_variables[:index]])
            gene = individual[sum_bits: sum_bits + design_variable.bits]
            value = design_variable.convert_gene_to_value(gene)
            variable_names = design_variable.get_variable_names()

            # in case a variable_name is a list created from a range of blocks
            block_variable_value = {**block_variable_value, **dict.fromkeys(variable_names, value)}

        return block_variable_value

    def update_model_parameters(self, decoded_chromosome: Dict) -> List[Dict]:
        """ Method updating model parameters given as ROXIE block definitions. Typically, it is a relative block
        definition.

        :param decoded_chromosome: a dictionary with keys containing a parameter name and block separated with a colon
        :return: an updated list of block definitions
        """
        blocks_def_update = deepcopy(self.block_inputs)
        for block_variable, value in decoded_chromosome.items():
            if ':' in block_variable:
                block, variable = block_variable.split(':')
                block = int(block)
                blocks_def_update[block - 1][variable] = value

        # Remove empty blocks
        return [block for block in blocks_def_update if block['nco'] > 0]

    def calculate_figures_of_merit(self, individual: List[int]) -> dict:
        """Method calculating figures of merit with scripts or notebooks (`papermill` and scrapbook packages).

        :param individual: a list of 0s and 1s representing an individual to be executed
        :return: a dictionary with figures of merit if the computation was successful, otherwise an dictionary with NaNs
        """
        # ToDo: Move to ModelExecutor
        # Retrieve global parameters
        decoded_chromosome = self.decode_individual(individual)
        global_design_variables = {key: value for (key, value) in decoded_chromosome.items() if ':' not in key}

        fom_dct = {}

        for notebook_config in self.config.notebooks:
            notebook_folder = notebook_config.notebook_folder
            notebook_name = notebook_config.notebook_name
            notebook_dir = os.path.join(self.output_subdirectory_dir, notebook_folder)

            # copy artefacts
            for dest, source in notebook_config.input_artefacts.items():
                copyfile(os.path.join(self.output_subdirectory_dir, source),
                         os.path.join(notebook_dir, dest))

            # set parameters
            parameters_dct = RoxieGeneticOptimization.merge_input_parameters(fom_dct,
                                                                             notebook_config,
                                                                             global_design_variables)

            # execute model
            fom_model = ModelExecutorFactory.build(self.is_script_executed). \
                execute(notebook_dir, notebook_name, parameters_dct)

            # if the error key is present in an output dictionary, an dictionary with NaNs is returned and loop is ended
            if ERROR_KEY in fom_model:
                return {objective_config.objective: float('nan') for objective_config in self.config.objectives}

            fom_dct = {**fom_dct, **fom_model}

        return fom_dct

    @staticmethod
    def merge_input_parameters(fom_dct: dict,
                               notebook_config: OptimizationNotebookConfig,
                               global_design_variables: dict) -> dict:
        """ Static method merging input parameters prior to an optimization routine execution.

        :param fom_dct: a dictionary with figures of merit calculated with scripts/notebooks
        :param notebook_config: a notebook config with input parameters dictionary
        :param global_design_variables: a dictionary with global design variables
        :return:
        """
        parameters_dct = {'full_output': False}
        for dest, source in notebook_config.input_parameters.items():
            if source in fom_dct.keys():
                parameters_dct[dest] = fom_dct[source]
            elif source in global_design_variables.keys():
                parameters_dct[dest] = global_design_variables[source]
        return parameters_dct
