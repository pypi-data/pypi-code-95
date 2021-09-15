from unittest import TestCase

from magnumapi.optimization.OptimizationConfig import OptimizationConfig
from tests.resource_files import create_resources_file_path


class TestOptimizationConfig(TestCase):
    def setUp(self) -> None:
        json_path = create_resources_file_path('resources/optimization/config.json')
        self.config = OptimizationConfig.initialize_config(json_path)

    def test_initialize_config(self):
        # arrange
        # act
        # assert
        self.assertEqual('/home/mmaciejewski/gitlab/magnum-nb/', self.config.input_folder)
        self.assertEqual('/home/mmaciejewski/gitlab/magnum-nb/output/', self.config.output_folder)
        self.assertEqual('optimization/GeneticOptimization.csv', self.config.logger_rel_path)

        self.assertEqual(100, self.config.n_gen)
        self.assertEqual(20, self.config.n_pop)
        self.assertAlmostEqual(0.9, self.config.r_cross, places=1)
        self.assertAlmostEqual(0.01, self.config.r_mut, places=2)

        self.assertEqual('b3', self.config.objectives[0].objective)
        self.assertAlmostEqual(0.1, self.config.objectives[0].weight, places=1)
        self.assertAlmostEqual(0.0, self.config.objectives[0].constraint, places=1)

        self.assertEqual('b5', self.config.objectives[1].objective)
        self.assertAlmostEqual(0.1, self.config.objectives[1].weight, places=1)
        self.assertAlmostEqual(0.0, self.config.objectives[1].constraint, places=1)

        self.assertEqual('margmi', self.config.objectives[2].objective)
        self.assertAlmostEqual(1, self.config.objectives[2].weight, places=0)
        self.assertAlmostEqual(0.85, self.config.objectives[2].constraint, places=2)

        self.assertEqual('seqv', self.config.objectives[3].objective)
        self.assertAlmostEqual(0.001, self.config.objectives[3].weight, places=3)
        self.assertAlmostEqual(0.0, self.config.objectives[3].constraint, places=1)

        self.assertEqual('geometry', self.config.notebooks[0].notebook_folder)
        self.assertEqual('Geometry.ipynb', self.config.notebooks[0].notebook_name)
        self.assertEqual({}, self.config.notebooks[0].input_parameters)
        self.assertEqual([], self.config.notebooks[0].output_parameters)
        self.assertEqual({}, self.config.notebooks[0].input_artefacts)
        self.assertEqual([], self.config.notebooks[0].output_artefacts)

        self.assertEqual('magnetic', self.config.notebooks[1].notebook_folder)
        self.assertEqual('ROXIE.ipynb', self.config.notebooks[1].notebook_name)
        self.assertEqual({}, self.config.notebooks[1].input_parameters)
        self.assertEqual(['b3', 'b5', 'bigb', 'margmi'], self.config.notebooks[1].output_parameters)
        self.assertEqual({}, self.config.notebooks[1].input_artefacts)
        self.assertEqual(['magnetic/input/roxie_scaled.force2d'],
                         self.config.notebooks[1].output_artefacts)

        self.assertEqual('mechanical', self.config.notebooks[2].notebook_folder)
        self.assertEqual('ANSYS.ipynb', self.config.notebooks[2].notebook_name)
        self.assertEqual({}, self.config.notebooks[2].input_parameters)
        self.assertEqual(['seqv', 'sxmn', 'syin', 'symn', 'syou'], self.config.notebooks[2].output_parameters)
        self.assertEqual({'input/roxie_scaled.force2d': 'magnetic/input/roxie_scaled.force2d'},
                         self.config.notebooks[2].input_artefacts)
        self.assertEqual([], self.config.notebooks[2].output_artefacts)

        self.assertEqual('thermal', self.config.notebooks[3].notebook_folder)
        self.assertEqual('MIITs.ipynb', self.config.notebooks[3].notebook_name)
        self.assertEqual({'peak_field': 'bigb'}, self.config.notebooks[3].input_parameters)
        self.assertEqual(['T_hotspot'], self.config.notebooks[3].output_parameters)
        self.assertEqual({}, self.config.notebooks[3].input_artefacts)
        self.assertEqual([], self.config.notebooks[3].output_artefacts)

    def test_get_weight(self):
        # arrange
        objective = 'b3'

        # act
        weight = self.config.get_weight(objective)

        # assert
        self.assertAlmostEqual(0.1, weight)

    def test_get_weight_error(self):
        # arrange
        objective = 'b7'

        # act
        with self.assertRaises(KeyError) as context:
            self.config.get_weight(objective)

        # assert
        self.assertTrue('Objective name b7 not present in objective configs.' in str(context.exception))

    def test_get_constraint(self):
        # arrange
        objective = 'b3'

        # act
        constraint = self.config.get_constraint(objective)

        # assert
        self.assertAlmostEqual(0, constraint)

    def test_get_constraint_error(self):
        # arrange
        objective = 'b7'

        # act
        with self.assertRaises(KeyError) as context:
            self.config.get_constraint(objective)

        # assert
        self.assertTrue('Objective name b7 not present in objective configs.' in str(context.exception))