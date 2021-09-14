from unittest import TestCase
from unittest.mock import patch

import pandas as pd
import numpy as np

from magnumapi.optimization.GeneticOptimization import GeneticOptimization
from magnumapi.optimization.constants import PENALTY
from tests.resource_files import create_resources_file_path

pop = [[1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1],
       [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0],
       [1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
       [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
       [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1],
       [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1],
       [1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0],
       [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

scores = [1, 1.2, 2, 2.5, 3, 3, 4, 5, 10, 20]

json_file_path = create_resources_file_path('resources/optimization/config.json')
csv_file_path = create_resources_file_path('resources/optimization/optim_input_enlarged.csv')
optimization_cfg = GeneticOptimization.initialize_config(json_file_path)
csv_path = create_resources_file_path('resources/optimization/GeneticOptimization.csv')
logger_df = pd.read_csv(csv_path, index_col=0)
logger_lst = [pd.DataFrame(record, index=[0]) for record in logger_df.to_dict('records')]


class TestGeneticOptimization(TestCase):

    @patch.multiple(GeneticOptimization, __abstractmethods__=set())
    def setUp(self) -> None:
        self.gen_opt = GeneticOptimization(optimization_cfg, pd.read_csv(csv_file_path))
        self.gen_opt.logger.logs = logger_lst

    def test_initialize_config(self):
        # arrange

        # act

        # assert
        self.assertEqual('/home/mmaciejewski/gitlab/magnum-nb/', optimization_cfg.input_folder)
        self.assertEqual('/home/mmaciejewski/gitlab/magnum-nb/output/', optimization_cfg.output_folder)
        self.assertEqual('optimization/GeneticOptimization.csv', optimization_cfg.logger_rel_path)

        self.assertEqual(100, optimization_cfg.n_gen)
        self.assertEqual(20, optimization_cfg.n_pop)
        self.assertAlmostEqual(0.9, optimization_cfg.r_cross, places=1)
        self.assertAlmostEqual(0.01, optimization_cfg.r_mut, places=2)

        self.assertEqual('b3', optimization_cfg.objectives[0].objective)
        self.assertAlmostEqual(0.1, optimization_cfg.objectives[0].weight, places=1)
        self.assertAlmostEqual(0.0, optimization_cfg.objectives[0].constraint, places=1)

        self.assertEqual('b5', optimization_cfg.objectives[1].objective)
        self.assertAlmostEqual(0.1, optimization_cfg.objectives[1].weight, places=1)
        self.assertAlmostEqual(0.0, optimization_cfg.objectives[1].constraint, places=1)

        self.assertEqual('margmi', optimization_cfg.objectives[2].objective)
        self.assertAlmostEqual(1, optimization_cfg.objectives[2].weight, places=0)
        self.assertAlmostEqual(0.85, optimization_cfg.objectives[2].constraint, places=2)

        self.assertEqual('seqv', optimization_cfg.objectives[3].objective)
        self.assertAlmostEqual(0.001, optimization_cfg.objectives[3].weight, places=3)
        self.assertAlmostEqual(0.0, optimization_cfg.objectives[3].constraint, places=1)

        self.assertEqual('geometry', optimization_cfg.notebooks[0].notebook_folder)
        self.assertEqual('Geometry.ipynb', optimization_cfg.notebooks[0].notebook_name)
        self.assertEqual({}, optimization_cfg.notebooks[0].input_parameters)
        self.assertEqual([], optimization_cfg.notebooks[0].output_parameters)
        self.assertEqual({}, optimization_cfg.notebooks[0].input_artefacts)
        self.assertEqual([], optimization_cfg.notebooks[0].output_artefacts)

        self.assertEqual('magnetic', optimization_cfg.notebooks[1].notebook_folder)
        self.assertEqual('ROXIE.ipynb', optimization_cfg.notebooks[1].notebook_name)
        self.assertEqual({}, optimization_cfg.notebooks[1].input_parameters)
        self.assertEqual(['b3', 'b5', 'bigb', 'margmi'], optimization_cfg.notebooks[1].output_parameters)
        self.assertEqual({}, optimization_cfg.notebooks[1].input_artefacts)
        self.assertEqual(['magnetic/input/roxie_scaled.force2d'],
                         optimization_cfg.notebooks[1].output_artefacts)

        self.assertEqual('mechanical', optimization_cfg.notebooks[2].notebook_folder)
        self.assertEqual('ANSYS.ipynb', optimization_cfg.notebooks[2].notebook_name)
        self.assertEqual({}, optimization_cfg.notebooks[2].input_parameters)
        self.assertEqual(['seqv', 'sxmn', 'syin', 'symn', 'syou'], optimization_cfg.notebooks[2].output_parameters)
        self.assertEqual({'input/roxie_scaled.force2d': 'magnetic/input/roxie_scaled.force2d'},
                         optimization_cfg.notebooks[2].input_artefacts)
        self.assertEqual([], optimization_cfg.notebooks[2].output_artefacts)

        self.assertEqual('thermal', optimization_cfg.notebooks[3].notebook_folder)
        self.assertEqual('MIITs.ipynb', optimization_cfg.notebooks[3].notebook_name)
        self.assertEqual({'peak_field': 'bigb'}, optimization_cfg.notebooks[3].input_parameters)
        self.assertEqual(['T_hotspot'], optimization_cfg.notebooks[3].output_parameters)
        self.assertEqual({}, optimization_cfg.notebooks[3].input_artefacts)
        self.assertEqual([], optimization_cfg.notebooks[3].output_artefacts)

    def test_str_config(self):
        # arrange

        # act

        # assert
        str_repr_ref_path = create_resources_file_path('resources/optimization/config_str_representation_ref.txt')

        with open(str_repr_ref_path, 'r') as file:
            str_repr_ref = file.read()

        self.assertEqual(str_repr_ref, str(optimization_cfg))

    def test_get_logger_df(self):
        # arrange

        # act
        logger_df_act = self.gen_opt.get_logger_df()

        # assert
        pd.testing.assert_frame_equal(logger_df, logger_df_act)

    def test_get_mean_fitness_per_generation(self):
        # arrange

        # act
        logger_mean_df_act = self.gen_opt.get_mean_fitness_per_generation()

        # assert
        logger_mean_df_csv_path = create_resources_file_path('resources/optimization/GeneticOptimizationMean.csv')
        logger_mean_df = pd.read_csv(logger_mean_df_csv_path, index_col=0)
        pd.testing.assert_frame_equal(logger_mean_df, logger_mean_df_act)

    def test_get_min_fitness_per_generation(self):
        # arrange

        # act
        logger_min_df_act = self.gen_opt.get_min_fitness_per_generation()

        # assert
        logger_min_df_csv_path = create_resources_file_path('resources/optimization/GeneticOptimizationMin.csv')
        logger_mean_df = pd.read_csv(logger_min_df_csv_path, index_col=0)
        pd.testing.assert_frame_equal(logger_mean_df, logger_min_df_act)

    def test_create_new_generation_without_elitism(self):
        # arrange
        np.random.seed(0)

        # act
        self.gen_opt.n_elite = 0
        pop_act = self.gen_opt.update_generation(pop, scores)

        # assert
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1], pop_act[0])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1], pop_act[1])
        self.assertListEqual([1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1], pop_act[2])
        self.assertListEqual([0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0], pop_act[3])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], pop_act[4])
        self.assertListEqual([1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0], pop_act[5])
        self.assertListEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], pop_act[6])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], pop_act[7])
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1], pop_act[8])
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1], pop_act[9])

    def test_create_new_generation_with_elitism(self):
        # arrange
        np.random.seed(0)

        # act
        self.gen_opt.n_elite = 2
        pop_act = self.gen_opt.update_generation(pop, scores)

        # assert
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1], pop_act[0])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], pop_act[1])
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1], pop_act[2])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1], pop_act[3])
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1], pop_act[4])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], pop_act[5])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], pop_act[6])
        self.assertListEqual([1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0], pop_act[7])
        self.assertListEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], pop_act[8])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], pop_act[9])

    def test_selection(self):
        # arrange
        np.random.seed(0)

        # act
        individual = GeneticOptimization.selection(pop, scores)

        # assert
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1], individual)

    def test_crossover(self):
        # arrange
        np.random.seed(0)

        p1 = [1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1]
        p2 = [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0]

        # act
        c = self.gen_opt.crossover(p1, p2)

        # assert
        self.assertListEqual([1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0], c[0])
        self.assertListEqual([0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1], c[1])

    def test_mutation(self):
        # arrange
        np.random.seed(0)
        chromosome = 10 * [1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1]

        # act
        mutated_chromosome = self.gen_opt.mutation(chromosome)

        # assert
        mutated_chromosome_ref = [1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0,
                                  1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0,
                                  1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0,
                                  1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1]

        self.assertEqual(mutated_chromosome_ref, mutated_chromosome)

    def test_calculate_score_with_nan(self):
        # arrange
        fom_dct = {'b3': float('nan'), 'b5': float('nan'), 'margmi': float('nan'), 'seqv': float('nan')}

        # act
        score = self.gen_opt.calculate_score(fom_dct)

        # assert
        self.assertEqual(PENALTY, score)

    def test_calculate_score(self):
        # arrange
        fom_dct = {'b3': 10.5, 'b5': 200, 'margmi': 10, 'seqv': 111}

        # act
        score = self.gen_opt.calculate_score(fom_dct)

        # assert
        self.assertAlmostEqual(30.311, score, places=5)
