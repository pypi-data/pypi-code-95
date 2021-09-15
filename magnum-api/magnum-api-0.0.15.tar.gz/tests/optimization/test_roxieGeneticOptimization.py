from unittest import TestCase

import pandas as pd
import numpy as np

from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.geometry.roxie.CableDatabase import CableDatabase
from magnumapi.optimization.GeneticOptimization import GeneticOptimization, RoxieGeneticOptimization
from tests.resource_files import create_resources_file_path

json_file_path = create_resources_file_path('resources/optimization/config.json')
csv_file_path = create_resources_file_path('resources/optimization/optim_input_enlarged.csv')
optimization_cfg = GeneticOptimization.initialize_config(json_file_path)

json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_rel.json')
cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
cadata = CableDatabase.read_cadata(cadata_path)
block_inputs = GeometryFactory.read_json_file(json_path)


class TestRoxieGeneticOptimization(TestCase):

    def setUp(self) -> None:
        self.gen_opt = RoxieGeneticOptimization(config=optimization_cfg,
                                                design_variables_df=pd.read_csv(csv_file_path),
                                                block_inputs=block_inputs,
                                                model_input_path='',
                                                is_script_executed=True,
                                                output_subdirectory_dir='')

    def test_initialize_population(self):
        # arrange
        np.random.seed(0)

        # act
        pop = self.gen_opt.initialize_population()

        # assert
        pop_ref = [0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0,
                   1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0,
                   0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0,
                   0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]

        self.assertListEqual(pop_ref, pop[0])

    def test_decode_chromosome(self):
        # arrange
        np.random.seed(0)

        # act
        pop = self.gen_opt.initialize_population()
        chromosome = self.gen_opt.decode_individual(pop[0])

        # assert
        chromosome_ref = {'2:phi_r': 5.953125, '3:phi_r': 9.78125, '4:phi_r': 4.75, '6:phi_r': 5.40625,
                          '7:phi_r': 6.28125, '9:phi_r': 7.703125, '10:phi_r': 5.734375, '12:phi_r': 6.390625,
                          '2:alpha_r': 3.59375, '3:alpha_r': 6.40625, '4:alpha_r': 6.5625, '6:alpha_r': 0.46875,
                          '7:alpha_r': 0.9375, '9:alpha_r': 5.78125, '10:alpha_r': 9.6875, '12:alpha_r': 7.8125,
                          '1:nco': 3, '2:nco': 2, '3:nco': 1, '4:nco': 0, '5:nco': 6, '6:nco': 9, '7:nco': 0,
                          '8:nco': 14, '9:nco': 9, '10:nco': 3, '11:nco': 30, '12:nco': 12}

        self.assertDictEqual(chromosome_ref, chromosome)

    def test_decode_chromosome_with_global_parameter(self):
        # arrange
        np.random.seed(0)
        csv_global_file_path = create_resources_file_path('resources/optimization/optim_input_enlarged_with_global.csv')
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        # act
        pop = self.gen_opt.initialize_population()
        chromosome = self.gen_opt.decode_individual(pop[0])

        # assert
        chromosome_ref = {'2:phi_r': 5.953125, '3:phi_r': 9.78125, '4:phi_r': 4.75, '6:phi_r': 5.40625,
                          '7:phi_r': 6.28125, '9:phi_r': 7.703125, '10:phi_r': 5.734375, '12:phi_r': 6.390625,
                          '2:alpha_r': 3.59375, '3:alpha_r': 6.40625, '4:alpha_r': 6.5625, '6:alpha_r': 0.46875,
                          '7:alpha_r': 0.9375, '9:alpha_r': 5.78125, '10:alpha_r': 9.6875, '12:alpha_r': 7.8125,
                          '1:nco': 3, '2:nco': 2, '3:nco': 1, '4:nco': 0, '5:nco': 6, '6:nco': 9, '7:nco': 0,
                          '8:nco': 14, '9:nco': 9, '10:nco': 3, '11:nco': 30, '12:nco': 12, 'R_EE': 1.2109375}

        self.assertDictEqual(chromosome_ref, chromosome)

    def test_decode_chromosome_with_global_parameter_multi_index(self):
        # arrange
        np.random.seed(0)
        path_str = 'resources/optimization/optim_input_enlarged_with_global_multi_index.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        # act
        pop = self.gen_opt.initialize_population()
        chromosome = self.gen_opt.decode_individual(pop[0])

        # assert
        chromosome_ref = {'2:phi_r': 5.953125, '3:phi_r': 9.78125, '4:phi_r': 4.75, '6:phi_r': 5.40625,
                          '7:phi_r': 6.28125, '9:phi_r': 7.703125, '10:phi_r': 5.734375, '12:phi_r': 6.390625,
                          '2:alpha_r': 3.59375, '3:alpha_r': 6.40625, '4:alpha_r': 6.5625, '6:alpha_r': 0.46875,
                          '7:alpha_r': 0.9375, '9:alpha_r': 5.78125, '10:alpha_r': 9.6875, '12:alpha_r': 7.8125,
                          '1:nco': 3, '2:nco': 2, '3:nco': 1, '4:nco': 0, '5:nco': 6, '6:nco': 9, '7:nco': 0,
                          '8:nco': 14, '9:nco': 9, '10:nco': 3, '11:nco': 30, '12:nco': 12, 'R_EE': 1.2109375,
                          '1:current': 12257.8125, '2:current': 12257.8125, '3:current': 12257.8125,
                          '4:current': 12257.8125, '5:current': 12257.8125, '6:current': 12257.8125,
                          '7:current': 12257.8125, '8:current': 12257.8125, '9:current': 12257.8125,
                          '10:current': 12257.8125, '11:current': 12257.8125, '12:current': 12257.8125}

        self.assertDictEqual(chromosome_ref, chromosome)

    def test_update_parameters(self):
        # arrange
        np.random.seed(0)

        # act
        pop = self.gen_opt.initialize_population()
        chromosome = self.gen_opt.decode_individual(pop[0])
        blocks_update_def = self.gen_opt.update_model_parameters(chromosome)

        # assert
        blocks_def_ref = [
            {'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 3, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha_r': 3.59375, 'phi_r': 5.953125, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha_r': 6.40625, 'phi_r': 9.78125, 'nco': 1, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha_r': 0.0, 'phi_r': 0.36728, 'nco': 6, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha_r': 0.46875, 'phi_r': 5.40625, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 14, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha_r': 5.78125, 'phi_r': 7.703125, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha_r': 9.6875, 'phi_r': 5.734375, 'nco': 3, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 30, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha_r': 7.8125, 'phi_r': 6.390625, 'nco': 12, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        self.assertListEqual(blocks_def_ref, blocks_update_def)

    def test_update_parameters_multi_index(self):
        # arrange
        np.random.seed(0)
        path_str = 'resources/optimization/optim_input_enlarged_with_global_multi_index.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        # act
        pop = self.gen_opt.initialize_population()
        chromosome = self.gen_opt.decode_individual(pop[0])
        blocks_update_def = self.gen_opt.update_model_parameters(chromosome)

        # assert
        blocks_def_ref = [
            {'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 3, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha_r': 3.59375, 'phi_r': 5.953125, 'nco': 2, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha_r': 6.40625, 'phi_r': 9.78125, 'nco': 1, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha_r': 0.0, 'phi_r': 0.36728, 'nco': 6, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha_r': 0.46875, 'phi_r': 5.40625, 'nco': 9, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 14, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha_r': 5.78125, 'phi_r': 7.703125, 'nco': 9, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha_r': 9.6875, 'phi_r': 5.734375, 'nco': 3, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 30, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha_r': 7.8125, 'phi_r': 6.390625, 'nco': 12, 'type': 1,
             'current': 12257.8125, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        self.assertListEqual(blocks_def_ref, blocks_update_def)
